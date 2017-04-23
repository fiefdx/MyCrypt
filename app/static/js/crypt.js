function cryptInit (user_locale) {
    var $table_header = $(".header-fixed > thead");
    var $table_header_tr = $(".header-fixed > thead > tr");
    var $table_body = $(".header-fixed > tbody");
    var $tasks_list = $("ul#tasks_list");
    var scrollBarSize = getBrowserScrollSize();
    var $path_bar = $("#path_bar");
    var $btn_status = $("#status");
    var $btn_settings = $("#settings");
    var $btn_settings_save = $("#settings_save");
    var $btn_home = $("#btn_home");
    var $btn_previous = $("#btn_previous");
    var $btn_refresh = $("#btn_refresh");
    var $btn_rename = $("#btn_rename");
    var $btn_copy = $("#btn_copy");
    var $btn_cut = $("#btn_cut");
    var $btn_paste = $("#btn_paste");
    var $btn_delete = $("#btn_delete");
    var $btn_encrypt = $("#btn_encrypt");
    var $btn_decrypt = $("#btn_decrypt");
    var $btn_hide = $("#btn_hide");
    var $btn_show = $("#btn_show");
    var $btn_rename_save = $("#rename_save");
    var $copy_modal_btn = $("#copy_modal_btn");
    var $cut_modal_btn = $("#cut_modal_btn");
    var $paste_modal_btn = $("#paste_modal_btn");
    var $btn_delete_delete = $("#delete_delete");
    var $encrypt_modal_btn = $("#encrypt_modal_btn");
    var $decrypt_modal_btn = $("#decrypt_modal_btn");
    var $hide_modal_btn = $("#hide_modal_btn");
    var $show_modal_btn = $("#show_modal_btn");
    var $home_path_input = $("#home_path");
    var $partitions_div = $("#partitions_div");
    var $display_en_passwd = $('#display_en_passwd');
    var $display_de_passwd = $('#display_de_passwd');
    var $display_hide_passwd = $('#display_hide_passwd');
    var $display_show_passwd = $('#display_show_passwd');

    var local = window.location.host;
    var uri = 'ws://' + local + '/websocket';
    console.log('Uri: ' + uri)

    var dir_path = [];
    var home_path = [];
    var home_path_string = "";
    var select_one_file = false;
    var select_multi_files = false;
    var select_one_dir = false;
    var select_multi_dirs = false;
    var disk_partitions = [];
    var dirs = [];
    var files = [];
    var columns = [];
    var dispaly_status = false;
    var sort = {'name':'name', 'desc':false};
    var warning_show = false;

    var WebSocket = window.WebSocket || window.MozWebSocket;
    if (WebSocket) {
        try {
            var socket = new WebSocket(uri);
        } catch (e) {}
    }

    if (socket) {
        socket.onopen = function() {
            console.log("websocket onopen");
            $btn_status.bind('click', displayStatusModal);
            $btn_settings.bind('click', settings);
            $btn_settings_save.bind('click', saveSettings);
            $btn_home.bind('click', goHomeDir);
            $btn_previous.bind('click', goPreviousDir);
            $btn_refresh.bind('click', refreshDir);
            $btn_rename.bind('click', displayRenameModal);
            $btn_rename_save.bind('click', renameFileDir);
            $btn_copy.bind('click', displayCopyModal);
            $copy_modal_btn.bind('click', copyFileDir);
            $btn_cut.bind('click', displayCutModal);
            $cut_modal_btn.bind('click', cutFileDir);
            $btn_paste.bind('click', displayPasteModal);
            $paste_modal_btn.bind('click', pasteFileDir);
            $btn_delete.bind('click', displayDeleteModal);
            $btn_delete_delete.bind('click', deleteFileDir);
            $btn_encrypt.bind('click', displayEncryptModal);
            $btn_decrypt.bind('click', displayDecryptModal);
            $display_en_passwd.bind('click', displayPassword);
            $display_de_passwd.bind('click', displayPassword);
            $display_hide_passwd.bind('click', displayPassword);
            $display_show_passwd.bind('click', displayPassword);
            $encrypt_modal_btn.bind('click', encryptFile);
            $decrypt_modal_btn.bind('click', decryptFile);
            $btn_hide.bind('click', displayHideModal);
            $btn_show.bind('click', displayShowModal);
            $hide_modal_btn.bind('click', hideFile);
            $show_modal_btn.bind('click', showFile);
            $btn_rename.attr("disabled", true);
            $btn_copy.attr("disabled", true);
            $btn_cut.attr("disabled", true);
            $btn_paste.attr("disabled", true);
            $btn_delete.attr("disabled", true);
            $btn_encrypt.attr("disabled", true);
            $btn_decrypt.attr("disabled", true);
            $btn_hide.attr("disabled", true);
            $btn_show.attr("disabled", true);
            $("#status_modal").on('hide.bs.modal', closeStatusData);
            $("#warning_modal").on('hide.bs.modal', function () {warning_show = false;});
        };

        socket.onmessage = function(msg) {
            console.log("websocket onmessage");
            var data = JSON.parse(msg.data);
            console.log(data);
            if (data.cmd == "refresh") {
                setTimeout(function(){location.reload();}, 1000);
            }

            if (data.cmd == "init") {
                columns = data.columns;
                $table_header_tr.empty();
                $table_body.empty();
                $path_bar.empty();
                $partitions_div.empty();
                data.columns.forEach(function (value, index, arrays) {
                    if (value.display && user_locale == "zh_CN") {
                        if (value.key == "name") {
                            $table_header_tr.append(
                                '<th id="' + value.key + '"><div class="outer"><div class="inner">&nbsp;<span><input class="select_all" type="checkbox"></span>&nbsp;' + 
                                value.trans + '&nbsp;&nbsp;</div></div></th>'
                            );
                        } else if (value.key == "num") {
                            var num = data.dirs.length + data.files.length;
                            $table_header_tr.append(
                                '<th id="' + value.key + '"><div class="outer"><div class="inner">&nbsp;' + value.trans + '&nbsp' + num + '&nbsp;&nbsp;</div></div></th>'
                            );
                        } else {
                            $table_header_tr.append(
                                '<th id="' + value.key + '"><div class="outer"><div class="inner">&nbsp;' + value.trans + '&nbsp;&nbsp;</div></div></th>'
                            );
                        }
                    } else if (value.display) {
                        if (value.key == "name") {
                            $table_header_tr.append(
                                '<th id="' + value.key + '"><div class="outer"><div class="inner">&nbsp;<span><input class="select_all" type="checkbox"></span>&nbsp;' + 
                                value.value + '&nbsp;&nbsp;</div></div></th>'
                            );
                        } else if (value.key == "num") {
                            var num = data.dirs.length + data.files.length;
                            $table_header_tr.append(
                                '<th id="' + value.key + '"><div class="outer"><div class="inner">&nbsp;' + value.value + '&nbsp' + num + '&nbsp;&nbsp;</div></div></th>'
                            );
                        } else {
                            $table_header_tr.append(
                                '<th id="' + value.key + '"><div class="outer"><div class="inner">&nbsp;' + value.value + '&nbsp;&nbsp;</div></div></th>'
                            );
                        }
                    }
                });
                displaySort(data.sort.name, data.sort.desc);
                $("th").bind('click', sortFileDir);
                data.dirs.forEach(function (value, index, arrays) {
                    var tr = '<tr id="table_item">';
                    for (var i=0; i<columns.length; i++) {
                        var col = columns[i];
                        if (col.key == 'num' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.num + '</div></div></td>';
                        } else if (col.key == 'name' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;<span><input class="dir_item" name="dir" id="dir_' + index + 
                                '" type="checkbox"></span>&nbsp;<span id="status_dir_' + value.sha1 + '" class="status"></span>' + '<span id="dir_' + index + 
                                '" class="dir_span glyphicon glyphicon-folder-close"></span><a class="dir_item" id="' + 
                                value.name + '">&nbsp;' + value.name + '</a></div></div></td>';
                        } else if (col.key == 'decrypt_name' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;</div></div></td>';
                        } else if (col.key == 'type' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.type + '</div></div></td>';
                        } else if (col.key == 'size' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.size + '</div></div></td>';
                        } else if (col.key == 'mtime' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.mtime + '</div></div></td>';
                        }
                    }
                    tr += '</tr>';
                    $table_body.append(tr);
                });
                dirs = data.dirs;
                data.files.forEach(function (value, index, arrays) {
                    var tr = '<tr id="table_item">';
                    for (var i=0; i<columns.length; i++) {
                        var col = columns[i];
                        if (col.key == 'num' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.num + '</div></div></td>';
                        } else if (col.key == 'name' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;<span><input class="file_item" name="file" id="file_' + index + 
                                '" type="checkbox"></span>&nbsp;<span id="status_file_' + value.sha1 + '" class="status"></span>' + 
                                '<span id="file_' + index + '" class="file_span glyphicon glyphicon-file"></span>&nbsp;' + 
                                value.name + '</div></div></td>';
                        } else if (col.key == 'decrypt_name' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.decrypt_name + '</div></div></td>';
                        } else if (col.key == 'type' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.type + '</div></div></td>';
                        } else if (col.key == 'size' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.size + '</div></div></td>';
                        } else if (col.key == 'mtime' && col.display) {
                            tr += '<td id="' + col.key + '"><div class="outer"><div class="inner">&nbsp;' + value.mtime + '</div></div></td>';
                        }
                    }
                    tr += '</tr>';
                    $table_body.append(tr);
                });
                files = data.files;
                data.dir_path.forEach(function (value, index, arrays) {
                    var string = "";
                    if (value == "/") {
                            value = "Root";
                        }
                    if (index == arrays.length - 1) {
                        string = '<li class="active">' + value + '<span id="disk_space">&nbsp;(' + data.disk_usage.free + 
                        '/' + data.disk_usage.total + ')' + '</span></li>';
                    }
                    else {
                        string = '<li><a id="dir_' + index + '" class="dir_name">' + value + '</a></li>';
                    }
                    $path_bar.append(string);
                });
                data.disk_partitions.forEach(function (value, index, arrays) {
                    $partitions_div.append(
                        '<a id="partition_' + index + '" class="list-group-item partition_a">' +
                        '<span class="glyphicon glyphicon-hdd"></span>' +
                        '<span id="partition_name">&nbsp;' + value.device + '</span>' +
                        '</a>'
                    )
                });
                disk_partitions = data.disk_partitions;
                $("a#partition_" + data.current_partition).addClass("active");
                dir_path = data.dir_path;
                home_path = data.home_path;
                home_path_string = data.home_path_string;
                $home_path_input.val(home_path_string);
                $("a.dir_name").bind('click', changeDir);
                $("a.dir_item").bind('click', openDir);
                $("a.partition_a").bind('click', changePartition);
                $("input[type=checkbox][name=dir]").bind('click', inputSelect);
                $("input[type=checkbox][name=file]").bind('click', inputSelect);
                $("input.select_all[type=checkbox]").bind('click', selectAll);
                $("tr#table_item").bind('click', selectOne);
                $btn_home.blur();
                $btn_previous.blur();
                $btn_refresh.blur();
                var tbody = document.getElementById("table_body");
                if (hasVerticalScrollBar(tbody)) {
                    $table_header.css({"margin-right": scrollBarSize.width});
                }
                else {
                    $table_header.css({"margin-right": 0});
                }
                var columns_keys = [];
                data.columns.forEach(function (value, index, arrays) {
                    if (value.display) {
                        columns_keys.push(value.key);
                    }
                });
                addCssDirsFiles(columns_keys);
                columnSelect(columns_keys);
            }

            if (data.cmd == "encrypting") {
                var sha1 = data.sha1;
                if (user_locale == "zh_CN") {
                    $("span#status_file_" + sha1).html("(加密-" + data.percent + "%)");
                } else {
                    $("span#status_file_" + sha1).html("(Encrypt-" + data.percent + "%)");
                }
            }

            if (data.cmd == "decrypting") {
                var sha1 = data.sha1;
                if (user_locale == "zh_CN") {
                    $("span#status_file_" + sha1).html("(解密-" + data.percent + "%)");
                } else {
                    $("span#status_file_" + sha1).html("(Decrypt-" + data.percent + "%)");
                }
            }

            if (data.cmd == "hiding") {
                var sha1 = data.sha1;
                if (user_locale == "zh_CN") {
                    $("span#status_file_" + sha1).html("(隐藏-" + data.percent + "%)");
                } else {
                    $("span#status_file_" + sha1).html("(Hide-" + data.percent + "%)");
                }
            }

            if (data.cmd == "showing") {
                var sha1 = data.sha1;
                if (user_locale == "zh_CN") {
                    $("span#status_file_" + sha1).html("(显示-" + data.percent + "%)");
                } else {
                    $("span#status_file_" + sha1).html("(Show-" + data.percent + "%)");
                }
            }

            if (data.cmd == "deleting") {
                var sha1 = data.sha1;
                var type = data.type;
                if (type == "file") {
                    if (user_locale == "zh_CN") {
                        $("span#status_file_" + sha1).html("(正在删除)");
                    } else {
                        $("span#status_file_" + sha1).html("(Deleting)");
                    }
                } else if (type == "dir") {
                    if (user_locale == "zh_CN") {
                        $("span#status_dir_" + sha1).html("(存在删除)");
                    } else {
                        $("span#status_dir_" + sha1).html("(Deleting)");
                    }
                }
            } else if (data.cmd == "deleted") {
                var sha1 = data.sha1;
                var type = data.type;
                if (type == "file") {
                    if (user_locale == "zh_CN") {
                        $("span#status_file_" + sha1).html("(删除成功)");
                    } else {
                        $("span#status_file_" + sha1).html("(Deleted)");
                    }
                } else if (type == "dir") {
                    if (user_locale == "zh_CN") {
                        $("span#status_dir_" + sha1).html("(删除成功)");
                    } else {
                        $("span#status_dir_" + sha1).html("(Deleted)");
                    }
                }
            }

            // if (data.cmd == "showing") {
            //     var sha1 = data.sha1;
            //     if (user_locale == "zh_CN") {
            //         $("span#status_file_" + sha1).html("(显示-" + data.percent + "%)");
            //     } else {
            //         $("span#status_file_" + sha1).html("(Show-" + data.percent + "%)");
            //     }
            // }

            if (data.cmd == "warning") {
                if (warning_show) {
                    $("div#warning_list").html($("div#warning_list").html() + '<p class="warning_item">' + data.info + '</p>');
                } else {
                    warning_show = true;
                    $("div#warning_list").html('<p class="warning_item">' + data.info + '</p>');
                    $('#warning_modal').modal('show');
                }
            }

            if (data.cmd == "paste") {
                $btn_paste.attr("disabled", false);
            }

            // if (data.cmd == "pasted") {
            //     $("span#warning_info").html(data.info);
            //     $('#warning_modal').modal('show');
            // }

            if (data.cmd == "status" && dispaly_status == true) {
                $tasks_list.empty();
                data.tasks.forEach(function (value, index, arrays) {
                    var li = '<li id="task_item" class="list-group-item">';
                    li += '<span id="task_name">' + value.name + '</span>'
                    li += '<span id="task_status" class="badge">' + value.status + '</span>';
                    li +='</li>'
                    $tasks_list.append(li);
                });
            }

            if (data.scrolltop) {
                $table_body.scrollTop(0);
            }
            checkSelect();
        };

        socket.onclose = function() {
            console.log("websocket onclose");
            $path_bar.css({'background-color' : '#CC0000'});
        };
    }

    function is_in(v, l) {
        for (var i=0; i<l.length; i++) {
            if (v == l[i]) {
                return true;
            }
        }
        return false;
    }

    function displaySort(th_id, desc) {
        if (desc) {
            $('th#' + th_id + ' > div > div.inner').append('<span class="glyphicon glyphicon-arrow-up order_arrow"></span>');
        } else {
            $('th#' + th_id + ' > div > div.inner').append('<span class="glyphicon glyphicon-arrow-down order_arrow"></span>');
        }
    }

    function sortFileDir() {
        var data = {};
        // console.log("Click TH");
        if (sort.name == $(this).attr("id")) {
            if (sort.desc == false) {
                sort.desc = true;
                $('th#' + $(this).attr("id") + ' > div > div.inner > span.order_arrow').remove();
                $('th#' + $(this).attr("id") + ' > div > div.inner').append('<span class="glyphicon glyphicon-arrow-up order_arrow"></span>');
            } else {
                sort.desc = false;
                $('th#' + $(this).attr("id") + ' > div > div.inner > span.order_arrow').remove();
                $('th#' + $(this).attr("id") + ' > div > div.inner').append('<span class="glyphicon glyphicon-arrow-down order_arrow"></span>');
            }
        } else {
            $('th#' + sort.name + ' > div > div.inner > span.order_arrow').remove();
            $('th#' + $(this).attr("id") + ' > div > div.inner > span.order_arrow').remove();
            sort.name = $(this).attr("id");
            sort.desc = false;
            $('th#' + $(this).attr("id") + ' > div > div.inner').append('<span class="glyphicon glyphicon-arrow-down order_arrow"></span>');
        }
        data.cmd = "refresh";
        data.dir_path = dir_path;
        data.sort = sort;
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function addCssDirsFiles(keys) {
        console.log("css: ", keys, "num" == keys[0]);
        var percent = 100.00;
        if (is_in('num', keys)) {
            $('th#num').css("width", "5%");
            $('td#num').css("width", "5%");
            percent -= 5.0;
            console.log("percent: ", percent);
        }
        if (is_in('type', keys)) {
            $('th#type').css("width", "5%");
            $('td#type').css("width", "5%");
            percent -= 5.0;
        }
        if (is_in('size', keys)) {
            $('th#size').css("width", "8%");
            $('td#size').css("width", "8%");
            percent -= 8.0;
        }
        if (is_in('mtime', keys)) {
            $('th#mtime').css("width", "8%");
            $('td#mtime').css("width", "8%");
            percent -= 8.0;
        }
        if (is_in('name', keys) && is_in('decrypt_name', keys)) {
            var width = percent/2.0;
            $('th#name').css("width", width + "%");
            $('td#name').css("width", width + "%");
            $('th#decrypt_name').css("width", width + "%");
            $('td#decrypt_name').css("width", width + "%");
        } else if (is_in('decrypt_name', keys)) {
            $('th#decrypt_name').css("width", percent + "%");
            $('td#decrypt_name').css("width", percent + "%");
        } else if (is_in('name', keys)) {
            $('th#name').css("width", percent + "%");
            $('td#name').css("width", percent + "%");
        }
    }

    function columnSelect(keys) {
        $("input.column[type=checkbox]:checked").each(function () {
            $("#" + $(this).attr("id") + ".btn").trigger("click");
        });
        for (var i=0; i<keys.length; i++) {
            $("#" + keys[i] + ".btn").trigger("click");
        }
    }

    function displayRenameModal() {
        var num = Number($("input[type=checkbox]:checked").attr("id").split("_")[1]);
        var type = $("input[type=checkbox]:checked").attr("id").split("_")[0];
        var file_name = "";
        if (type == "dir") {
            file_name = dirs[num].name;
        }
        else if (type == "file") {
            file_name = files[num].name;
        }
        $("input#new_name").val(file_name);
        $('#rename_modal').modal('show');
    }

    function renameFileDir() {
        var num = Number($("input[type=checkbox]:checked").attr("id").split("_")[1]);
        var type = $("input[type=checkbox]:checked").attr("id").split("_")[0];
        var old_name = "";
        if (type == "dir") {
            old_name = dirs[num].name;
        }
        else if (type == "file") {
            old_name = files[num].name;
        }
        var new_name = $("input#new_name").val();
        var data = {};
        data.cmd = "rename";
        data.old_name = old_name;
        data.new_name = new_name;
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
        clearAll();
    }

    function displayCopyModal() {
        $('#copy_modal').modal('show');
    }

    function copyFileDir() {
        var copy_dirs = [];
        var copy_files = [];
        var data = {}
        $("input[type=checkbox][name=dir]:checked").each(function () {
            var num = Number($(this).attr("id").split("_")[1])
            copy_dirs.push({"name":dirs[num].name, "sha1":dirs[num].sha1});
        });
        $("input[type=checkbox][name=file]:checked").each(function () {
            var num = Number($(this).attr("id").split("_")[1])
            copy_files.push({"name":files[num].name, "sha1":files[num].sha1});
        });
        data.cmd = "copy";
        data.dirs = copy_dirs;
        data.files = copy_files;
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
        // $("input[type=checkbox][name=dir]").prop('checked', false);
    }

    function displayCutModal() {
        $('#cut_modal').modal('show');
    }

    function cutFileDir() {
        var cut_dirs = [];
        var cut_files = [];
        var data = {}
        $("input[type=checkbox][name=dir]:checked").each(function () {
            var num = Number($(this).attr("id").split("_")[1])
            cut_dirs.push({"name":dirs[num].name, "sha1":dirs[num].sha1});
        });
        $("input[type=checkbox][name=file]:checked").each(function () {
            var num = Number($(this).attr("id").split("_")[1])
            cut_files.push({"name":files[num].name, "sha1":files[num].sha1});
        });
        data.cmd = "cut";
        data.dirs = cut_dirs;
        data.files = cut_files;
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
        // $("input[type=checkbox][name=dir]").prop('checked', false);
    }

    function displayPasteModal() {
        $('#paste_modal').modal('show');
    }

    function pasteFileDir() {
        var data = {}
        data.cmd = "paste";
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function displayDeleteModal() {
        $('#delete_modal').modal('show');
    }

    function deleteFileDir() {
        var delete_dirs = [];
        var delete_files = [];
        var data = {}
        $("input[type=checkbox][name=dir]:checked").each(function () {
            var num = Number($(this).attr("id").split("_")[1])
            delete_dirs.push({"name":dirs[num].name, "sha1":dirs[num].sha1});
        });
        $("input[type=checkbox][name=file]:checked").each(function () {
            var num = Number($(this).attr("id").split("_")[1])
            delete_files.push({"name":files[num].name, "sha1":files[num].sha1});
        });
        data.cmd = "delete";
        data.dirs = delete_dirs;
        data.files = delete_files;
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
        // $("input[type=checkbox][name=dir]").prop('checked', false);
    }

    function displayEncryptModal() {
        $('#encrypt_passwd').val("");
        $('#encrypt_modal').modal('show');
    }

    function encryptFile() {
        var num = Number($("input[type=checkbox]:checked").attr("id").split("_")[1]);
        var type = $("input[type=checkbox]:checked").attr("id").split("_")[0];
        var password = $("input#encrypt_passwd").val();
        var file_name = "";
        var data = {};
        if (type == "file") {
            file_name = files[num].name;
            data.cmd = "encrypt";
            data.file_name = file_name;
            data.dir_path = dir_path;
            data.password = password;
            data.sha1 = files[num].sha1;
            console.log(data);
            socket.send(JSON.stringify(data));
        }
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
    }

    function displayDecryptModal() {
        $('#decrypt_passwd').val("");
        $('#decrypt_modal').modal('show');
    }

    function decryptFile() {
        var num = Number($("input[type=checkbox]:checked").attr("id").split("_")[1]);
        var type = $("input[type=checkbox]:checked").attr("id").split("_")[0];
        var password = $("input#decrypt_passwd").val();
        var file_name = "";
        var data = {};
        if (type == "file") {
            file_name = files[num].name;
            data.cmd = "decrypt";
            data.file_name = file_name;
            data.dir_path = dir_path;
            data.password = password;
            data.sha1 = files[num].sha1;
            console.log(data);
            socket.send(JSON.stringify(data));
        }
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
    }

    function displayHideModal() {
        $('#hide_passwd').val("");
        $('#hide_modal').modal('show');
    }

    function hideFile() {
        var num = Number($("input[type=checkbox]:checked").attr("id").split("_")[1]);
        var type = $("input[type=checkbox]:checked").attr("id").split("_")[0];
        var password = $("input#hide_passwd").val();
        var file_name = "";
        var data = {};
        if (type == "file") {
            file_name = files[num].name;
            data.cmd = "hide";
            data.file_name = file_name;
            data.dir_path = dir_path;
            data.password = password;
            data.sha1 = files[num].sha1;
            console.log(data);
            socket.send(JSON.stringify(data));
        }
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
    }

    function displayShowModal() {
        $('#show_passwd').val("");
        $('#show_modal').modal('show');
    }

    function showFile() {
        var num = Number($("input[type=checkbox]:checked").attr("id").split("_")[1]);
        var type = $("input[type=checkbox]:checked").attr("id").split("_")[0];
        var password = $("input#show_passwd").val();
        var file_name = "";
        var data = {};
        if (type == "file") {
            file_name = files[num].name;
            data.cmd = "show";
            data.file_name = file_name;
            data.dir_path = dir_path;
            data.password = password;
            data.sha1 = files[num].sha1;
            console.log(data);
            socket.send(JSON.stringify(data));
        }
        clearAll();
        // $("input[type=checkbox][name=file]").prop('checked', false);
    }

    function displayPassword() {
        var dispass = $(this).val();
        if (dispass == "unable") {
            $(this).val("enable");
            if ($(this).attr("id") == 'display_en_passwd') {
                document.getElementById("encrypt_passwd").type = "text";
            } else if ($(this).attr("id") == 'display_de_passwd') {
                document.getElementById("decrypt_passwd").type = "text";
            } else if ($(this).attr("id") == 'display_hide_passwd') {
                document.getElementById("hide_passwd").type = "text";
            } else if ($(this).attr("id") == 'display_show_passwd') {
                document.getElementById("show_passwd").type = "text";
            }
        }
        else {
            $(this).val("unable");
            if ($(this).attr("id") == 'display_en_passwd') {
                document.getElementById("encrypt_passwd").type = "password";
            } else if ($(this).attr("id") == 'display_de_passwd') {
                document.getElementById("decrypt_passwd").type = "password";
            } else if ($(this).attr("id") == 'display_hide_passwd') {
                document.getElementById("hide_passwd").type = "password";
            } else if ($(this).attr("id") == 'display_show_passwd') {
                document.getElementById("show_passwd").type = "password";
            }
        }
    }

    function goHomeDir() {
        var data = {};
        data.cmd = "cd";
        data.dir_path = home_path;
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function goPreviousDir() {
        var index = dir_path.length - 1;
        var data = {};
        data.cmd = "cd";
        if (index == 0) {
            index = 1;
        }
        data.dir_path = dir_path.slice(0, index);
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function refreshDir() {
        var data = {};
        data.cmd = "refresh";
        data.sort = sort;
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function changeDir() {
        var index = Number($(this).attr("id").split("_")[1]) + 1;
        var data = {};
        data.cmd = "cd";
        data.dir_path = dir_path.slice(0, index);
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function openDir(event) {
        var dir_name = $(this).attr("id");
        console.log("dir_name: " + dir_name);
        var data = {};
        data.cmd = "cd";
        dir_path.push(dir_name);
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
        event.stopPropagation()
    }

    function changePartition() {
        var partition_num = Number($(this).attr("id").split("_")[1]);
        var dir_path = disk_partitions[partition_num].mountpoint;
        var data = {};
        data.cmd = "cd";
        data.dir_path = dir_path;
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function displayStatusModal() {
        dispaly_status = true;
        var data = {};
        data.cmd = "status";
        data.enable = true;
        console.log(data);
        socket.send(JSON.stringify(data));
        $('#status_modal').modal('show');
    }

    function closeStatusData() {
        dispaly_status = false;
        var data = {};
        data.cmd = "status";
        data.enable = false;
        console.log(data);
        socket.send(JSON.stringify(data));
    }

    function settings() {
        $('#settings_modal').modal('show');
    }

    function saveSettings() {
        var display_true_list = [];
        columns.forEach(function (value, index, arrays) {
            value.display = false;
        });
        $("input.column[type=checkbox]:checked").each(function () {
            display_true_list.push($(this).attr("id"));
            console.log("check_column: ", $(this).attr("id"));
        });
        columns.forEach(function (value, index, arrays) {
            if (is_in(value.key, display_true_list)) {
                value.display = true;
                console.log("value: ", value.value);
            }
        });
        var data = {};
        data.cmd = "set";
        data.language = document.querySelector('input[name="optionsRadios"]:checked').value;
        data.home_path = $("#home_path").val();
        data.password = $("#passwd").val();
        data.dir_path = dir_path
        data.columns = columns;
        console.log(data);
        socket.send(JSON.stringify(data));
        $('#settings_modal').modal('hide');
    }

    function selectOne(event) {
        if ($(this).find("input[type=checkbox]:checked").length) {
            $(this).find("input[type=checkbox]").prop('checked', false);
            $(this).removeClass("success");
        } else {
            $(this).find("input[type=checkbox]").prop('checked', true);
            $(this).addClass("success");
        }
        checkSelect();
        event.stopPropagation()
    }

    function inputSelect(event) {
        console.log("input select: ", this.checked);
        if (this.checked) {
            $(this).parent("span").parent("div").parent("div").parent("td").parent("tr").addClass("success");
        } else {
            $(this).parent("span").parent("div").parent("div").parent("td").parent("tr").removeClass("success");
        }
        checkSelect();
        event.stopPropagation()
    }

    function selectAll(event) {
        if ($("input.select_all[type=checkbox]:checked").length) {
            $("input[type=checkbox][name=dir]").prop('checked', this.checked);
            $("input[type=checkbox][name=dir]").parent("span").parent("div").parent("div").parent("td").parent("tr").addClass("success");
            $("input[type=checkbox][name=file]").prop('checked', this.checked);
            $("input[type=checkbox][name=file]").parent("span").parent("div").parent("div").parent("td").parent("tr").addClass("success");
        } else {
            $("input[type=checkbox][name=dir]").prop('checked', false);
            $("input[type=checkbox][name=dir]").parent("span").parent("div").parent("div").parent("td").parent("tr").removeClass("success");
            $("input[type=checkbox][name=file]").prop('checked', false);
            $("input[type=checkbox][name=file]").parent("span").parent("div").parent("div").parent("td").parent("tr").removeClass("success");
        }
        checkSelect();
        event.stopPropagation()
    }

    function clearAll(event) {
        $("input[type=checkbox][name=dir]").prop('checked', false);
        $("input[type=checkbox][name=dir]").parent("span").parent("div").parent("div").parent("td").parent("tr").removeClass("success");
        $("input[type=checkbox][name=file]").prop('checked', false);
        $("input[type=checkbox][name=file]").parent("span").parent("div").parent("div").parent("td").parent("tr").removeClass("success");
        checkSelect();
        event.stopPropagation()
    }

    function checkSelect(event) {
        var num_dir = 0;
        var num_file = 0;
        $("input[type=checkbox][name=dir]:checked").each(function () {
            num_dir++;
        });
        $("input[type=checkbox][name=file]:checked").each(function () {
            num_file++;
        });
        if (num_file == 1 && num_dir == 0) {
            $btn_rename.attr("disabled", false);
            $btn_copy.attr("disabled", false);
            $btn_cut.attr("disabled", false);
            // $btn_paste.attr("disabled", true);
            $btn_delete.attr("disabled", false);
            $btn_encrypt.attr("disabled", false);
            $btn_decrypt.attr("disabled", false);
            $btn_hide.attr("disabled", false);
            $btn_show.attr("disabled", false);
        }
        else if (num_file > 1) {
            $btn_rename.attr("disabled", true);
            $btn_copy.attr("disabled", false);
            $btn_cut.attr("disabled", false);
            // $btn_paste.attr("disabled", true);
            $btn_delete.attr("disabled", false);
            $btn_encrypt.attr("disabled", true);
            $btn_decrypt.attr("disabled", true);
            $btn_hide.attr("disabled", true);
            $btn_show.attr("disabled", true);
        }
        else if (num_file == 0 && num_dir == 1) {
            $btn_rename.attr("disabled", false);
            $btn_copy.attr("disabled", false);
            $btn_cut.attr("disabled", false);
            // $btn_paste.attr("disabled", true);
            $btn_delete.attr("disabled", false);
            $btn_encrypt.attr("disabled", true);
            $btn_decrypt.attr("disabled", true);
            $btn_hide.attr("disabled", true);
            $btn_show.attr("disabled", true);
        }
        else if (num_file == 0 && num_dir == 0) {
            $btn_rename.attr("disabled", true);
            $btn_copy.attr("disabled", true);
            $btn_cut.attr("disabled", true);
            // $btn_paste.attr("disabled", true);
            $btn_delete.attr("disabled", true);
            $btn_encrypt.attr("disabled", true);
            $btn_decrypt.attr("disabled", true);
            $btn_hide.attr("disabled", true);
            $btn_show.attr("disabled", true);
        }
        else {
            $btn_rename.attr("disabled", true);
            $btn_copy.attr("disabled", false);
            $btn_cut.attr("disabled", false);
            // $btn_paste.attr("disabled", true);
            $btn_delete.attr("disabled", false);
            $btn_encrypt.attr("disabled", true);
            $btn_decrypt.attr("disabled", true);
            $btn_hide.attr("disabled", true);
            $btn_show.attr("disabled", true);
        }
        if (event){
            event.stopPropagation()
        }
    }

    function hasVerticalScrollBar(el) {
        var result = el.scrollHeight > el.clientHeight;
        return result;
    }

    function getBrowserScrollSize() {
        var css = {
            "border":  "none",
            "height":  "200px",
            "margin":  "0",
            "padding": "0",
            "width":   "200px"
        };

        var inner = $("<div>").css($.extend({}, css));
        var outer = $("<div>").css($.extend({
            "left":       "-1000px",
            "overflow":   "scroll",
            "position":   "absolute",
            "top":        "-1000px"
        }, css)).append(inner).appendTo("body")
        .scrollLeft(1000)
        .scrollTop(1000);

        var scrollSize = {
            "height": (outer.offset().top - inner.offset().top) || 0,
            "width": (outer.offset().left - inner.offset().left) || 0
        };

        outer.remove();
        return scrollSize;
    }
}