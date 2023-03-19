import os
import requests
import subprocess
import re
import pickle
import sys
import logging
from lxml import etree
from urllib.parse import urljoin
from PySide6.QtWidgets import QMainWindow, QApplication, QLabel, QTableWidgetItem
from ui import Ui_MainWindow
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, QModelIndex, QUrl, QThread, Signal
from PySide6.QtNetwork import QNetworkCookie
from urllib.parse import urlencode

debug = True
gender = 0  # 0: male  1: female


class HoldTcp(QThread):
    finish = Signal()

    def __init__(self, session: requests.Session, appid: str, rand_token: str, sid: str):
        super().__init__()
        self.session = session
        self.appid = appid
        self.rand_token = rand_token
        self.sid = sid

    def run(self) -> None:
        url4 = "https://sis.ustb.edu.cn/connect/state"
        url5 = "https://jwgl.ustb.edu.cn/glht/Logon.do"
        resp4 = self.session.get(url4, params={'sid': self.sid})
        resp4 = self.session.get(url4, params={'sid': self.sid})
        auth_code = resp4.json()['data']
        params5 = {
            'method': 'weCharLogin',
            'appid': self.appid,
            'auth_code': auth_code,
            'rand_token': self.rand_token
        }
        resp5 = self.session.get(url5, params=params5)

        logging.log(logging.INFO, "Successfully Login")
        with open("cookies.pkl", "wb") as f:
            pickle.dump(self.session.cookies, f)
        logging.info("Cookies saved")
        return self.finsh2emit()

    def finsh2emit(self):
        self.finish.emit()


def show_qrcode_method_1(resp_content: bytes) -> None:
    with open("qrcode.jpg", "wb") as f:
        f.write(resp_content)
    cmd = {'linux': 'xdg-open',
           'win32': 'explorer',
           'darwin': 'open'}[sys.platform]
    subprocess.run([cmd, "qrcode.jpg"])


def load_cookies_from_jar(session: requests.Session):
    cookie = QNetworkCookie()
    cookie.setName("JSESSIONID".encode())
    cookie.setValue(session.cookies.get("JSESSIONID", domain="jwgl.ustb.edu.cn", path="/").encode())
    cookie.setDomain("jwgl.ustb.edu.cn")
    cookie.setPath("/")
    yield cookie
    cookie = QNetworkCookie()
    cookie.setName("JSESSIONID".encode())
    cookie.setValue(session.cookies.get("JSESSIONID", domain="jwgl.ustb.edu.cn", path="/").encode())
    cookie.setDomain("jwgl.ustb.edu.cn")
    cookie.setPath("/glht")
    yield cookie
    cookie = QNetworkCookie()
    cookie.setName("SERVERID".encode())
    cookie.setValue(session.cookies.get("SERVERID", domain="jwgl.ustb.edu.cn", path="/").encode())
    cookie.setDomain("jwgl.ustb.edu.cn")
    cookie.setPath("/")
    yield cookie


class MyWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent)
        self.course_dic = {}
        self.lst = []
        self.t = None
        self.setupUi(self)
        self.session = requests.Session()
        self.login()

    def login(self):
        if "cookies.pkl" in os.listdir():
            with open("cookies.pkl", "rb") as f:
                self.session.cookies.update(pickle.load(f))
                logging.info("Found cookie.pkl in current directory, Loading cookies...")
                return self.select_course()

        url1 = "https://jwgl.ustb.edu.cn/glht/Logon.do?method=randToken"
        url3 = "https://sis.ustb.edu.cn/connect/qrimg"
        url2 = "https://sis.ustb.edu.cn/connect/qrpage"
        params2 = {
            'appid': None,
            'return_url': 'https://jwgl.ustb.edu.cn/glht/Logon.do?method=weCharLogin',
            'rand_token': None,
            'embed_flag': 1
        }
        resp1 = self.session.post(url1)
        appid = resp1.json()['appid']
        rand_token = resp1.json()['rand_token']
        params2['appid'] = appid
        params2['rand_token'] = rand_token
        resp2 = self.session.get(url2, params=params2)
        match_obj = re.search(r'(?<=^\ssid = ")\w*(?=",)', resp2.text, re.MULTILINE)
        sid = match_obj.group()
        resp3 = self.session.get(url3, params={'sid': sid})
        self.show_image(resp3.content)
        logging.info("Waiting for scanning qrcode...")
        self.t = HoldTcp(self.session, appid, rand_token, sid)
        self.t.start()
        self.t.finish.connect(self.select_course)


    def select_course(self):
        with open("cookies.pkl", "rb") as f:
            self.session.cookies.update(pickle.load(f))
        url1 = "https://jwgl.ustb.edu.cn/xsxk/xsxkzx_index"
        url2 = "https://jwgl.ustb.edu.cn/xsxk/xsxkzx_zy"
        resp1 = self.session.get(url1)
        course_round = re.search(r"""(?<= onclick="jrxk\(')(\w*)(?='\);")""", resp1.text).group()  # 选课轮次
        logging.info("course_round match result: %s", course_round)
        params2 = {
            'type': 'zybxk',
            'xsid': None,
            'kcfalx': 'zx',
            'opener': 'zybxk',
            'dqjx0502zbid': course_round
        }
        resp2 = self.session.get(url2, params={'jx0502zbid': course_round})
        tree = etree.HTML(resp2.text)
        href = tree.xpath("//li/a/@href")[0]
        url3 = urljoin(url2, href)
        resp3 = self.session.get(url3)
        tree = etree.HTML(resp3.text)
        for table_row in tree.xpath('//table/tr')[1:]:
            choose_state = table_row.xpath("./td[10]/text()")[0].strip()
            tr_tag_class = table_row.xpath("./@class")[0].strip()
            if (choose_state == "未选" or debug) and "dqxkxqclass" in tr_tag_class:
                course_name = table_row.xpath("./td[4]/text()")[0].strip()
                click_func = table_row.xpath("./@onclick")[0].strip()
                match_res = re.search(
                    r"qhkc\(this,'(?P<jx02id>\w+)','(?P<zxfxct>\d)','(?P<kcsx>\d)','(?P<kcmc>.*?)'\);",
                    click_func)
                if match_res is None:
                    logging.warning("match result returned None\nstring: %s", click_func)
                    continue
                jx02id = match_res.group("jx02id")  # course id
                zxfxct = match_res.group("zxfxct")
                kcsx = match_res.group("kcsx")
                kcmc = match_res.group("kcmc")
                if "体育" in kcmc:  # pe： short for physical education
                    is_pe = 1
                else:
                    is_pe = 0
                self.course_dic[course_name] = {
                    'dqjx0502zbid': course_round,
                    'jx02id': jx02id,
                    'zxfxct': zxfxct,
                    'istyk': is_pe
                }
        self.course_table.setRowCount(len(self.course_dic))
        lst = list(self.course_dic.keys())
        for index, course_name in enumerate(lst):
            item = QTableWidgetItem(course_name)
            item.setFlags(Qt.ItemIsEnabled)
            self.course_table.setItem(index, 0, item)
        for cookie in load_cookies_from_jar(self.session):
            self.podium_webview.page().profile().cookieStore().setCookie(cookie)
        self.course_table.clicked.connect(lambda x: self.select_podium(x, self.course_dic, lst))
        # return course_dic[lst[index]]

    def select_podium(self, item: QModelIndex, course_dic: dict, lst: list):
        params: dict = course_dic[lst[item.row()]]
        url = "https://jwgl.ustb.edu.cn/xsxk/getkcxxlist.do"
        params1 = {
            # 'xsid': None,
            'dqjx0502zbid': None,
            'type': 'zybxk',
            'kcfalx': 'zx',
            'jx02id': None,
            'opener': 'zybxk',
            'zxfxct': None,
            'sfzybxk': 1,
            'istyk': None
        }
        params1 = {**params1, **params}
        url = url + '?' + urlencode(params1)
        self.podium_webview.setUrl(QUrl(url))

        # resp1 = self.session.get(url, params=params1)
        #
        # tree = etree.HTML(resp1.text)
        # xsid = tree.xpath("//*[@id='xsid']/@value")
        # type = tree.xpath("//*[@id='type']/@value")
        # kcfalx = tree.xpath("//*[@id='kcfalx']/@value")
        # jx02id = tree.xpath("//*[@id='jx02id']/@value")
        # zxfxct = tree.xpath("//*[@id='zxfxct']/@value")
        # sfzybxk = tree.xpath("//*[@id='sfzybxk']/@value")
        # cxtzdid = tree.xpath("//*[@id='cxtzdid']/@value")
        # kcxzdm = tree.xpath("//*[@id='kcxzdm']/@value")
        # dqjx0502zbid = tree.xpath("//*[@id='dqjx0502zbid']/@value")
        # istyk = tree.xpath("//*[@id='istyk']/@value")
        # podium_list = []
        # for table_row in tree.xpath("//table[@class='Nsb_r_list Nsb_table']/tr")[1:]:
        #     podium_name = table_row.xpath("./td[4]/a/text()")[0].strip()
        #     href_text = table_row.xpath("./td[2]/div/a[1]/@href")[0].strip()
        #     match_res = re.search(
        #         "javascript:xsxkOper\('(?P<name_a>\w*)','(?P<name_b>\w*)','(?P<name_c>\d*)','(?P<name_d>.*?)','(?P<name_e>\w*)'\);",
        #         href_text)
        #     name_a = match_res.group("name_a")
        #     name_b = match_res.group("name_b")
        #     name_c = match_res.group("name_c")
        #     name_d = match_res.group("name_d")
        #     name_e = match_res.group("name_e")
        #     podium_list.append({
        #         "podium_name": podium_name,
        #         "name_a": name_a,
        #         "name_b": name_b,
        #         "name_c": name_c,
        #         "name_d": name_d,
        #         "name_e": name_e,
        #     })
        #
        # pprint.pprint(podium_list)

    def show_image(self, resp_content):
        with open("qrcode.jpg", "wb") as f:
            f.write(resp_content)
        img = QPixmap("qrcode.jpg")
        img = img.scaledToWidth(self.label.width())
        img = img.scaledToHeight(self.label.height())
        self.label.setPixmap(img)
        # self.resize(img.width(), img.height())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())

