function qhkc(obj, jx02id, zxfxct, kcsx, kcmc) {
    $('#tableid tr').css({"background-color": ""});
    $('.dqxkxqclass').css({"background-color": "#FFFFE0"});
    $(obj).css({"background-color": "#C7E5FF"});
    var type = "zybxk";
    var sfzybxk = "0";
    if (type == "zybxk") {
        sfzybxk = "1";
    }
    if (type == "fxxk" && kcsx == "1") {
        sfzybxk = "1";
    }
    var istyk = "0";
    if (kcmc.indexOf("体育") >= 0) {
        istyk = "1";
    }
    parent.frames["kcxxFrame"].location.href = "/xsxk/getkcxxlist.do?xsid=&dqjx0502zbid=4C58AB65E74642428C187038C64AA9EF&type=zybxk&kcfalx=" + $("#kcfalx").val() + "&jx02id=" + jx02id + "&opener=zybxk&zxfxct=" + zxfxct + "&sfzybxk=" + sfzybxk + "&istyk=" + istyk;
}