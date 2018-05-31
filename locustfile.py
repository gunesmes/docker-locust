#!/usr/local/bin/python
# -*- coding: utf-8 -*-

from locust import HttpLocust, TaskSet, task
from pyquery import PyQuery
import random, requests, time, os, inspect, json, sys
from locust.clients import HttpSession
from locust import events
from locust.stats import *


sys.setrecursionlimit(100000000)


class UserBehaviour(TaskSet):
    address_payload = {'Title': '', 'CityName': 'ANKARA', 'CountyID': 1187, 'TaxOffice': '', 'IsCurrentInvoiceAddress': False, 'IdentityNo': '', 'AddressLocation': {'Districts': [], 'Cities': [], 'Counties': [], 'Countries': []}, 'ConsigneeLastName': 'Test', 'DistrictID': 0, 'IsPersonalInvoice': False, 'AddressLine2': ' ', 'DistrictName': '', 'Name': 'Performance Adres', 'AddressLine1': 'maslak mahallesi bla bla caddesi', 'CityID': 89, 'IsCurrentDeliveryAddress': False, 'ConsigneeFirstName': 'Performance', 'PostalCode': '06006 ', 'TaxNo': '', 'CountryID': 1, 'HomePhoneNo': '(222) 222 22 22', 'UsableForBilling': False, 'CountyName': 'BEYPAZARI', 'MobilePhoneNo': '(111) 111 11 11', 'CountryName': 'T\xc3\x9cRK\xc4\xb0YE'}
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'

    target_machine_ips = []

    # users
    users = [
            ["morhipojohndoewarmup@gmail.com", "Mor787878"],
        ]

    user_sessions = {}

    # sezon sayfasi
    sezon_links         = []
    kadin_links         = []
    erkek_links         = []
    ayakkabi_links      = []
    spor_links          = []
    cocuk_links         = []
    ev_links            = []
    kozmetik_links      = []
    markalar_links      = []
    sezon_urun_detay    = []

    # ps sayfası
    ps_links            = []
    ps_urun_detay       = []


    services = ["/mobile/v3/User/OrderList", 
                "/mobile/v3/Order/OrderAddresses", 
                "/mobile/v3/User/CouponList", 
                "/mobile/v3/User/MyFavorites", 
                "/mobile/v3/user/myreturnorders?history=0", 
                "/mobile/v3/User/UserInfo"
                ]
    
    # aktif kampayalardan gelen ps ürünleri listesi
    ps_active_campaign_product_list = []

    def get_urls(self, url, locator, key):
        links = []
        request = self.client.get(url, headers = { 'User-Agent': self.user_agent})

        pq = PyQuery(request.content)
        link_elements = pq(locator)
        for link in link_elements:
            if key in link.attrib and "http" not in link.attrib[key] and "avascript" not in link.attrib[key]:
                links.append(link.attrib[key].strip())

        return links

    def load_user_sessions(self):
        for ip in self.target_machine_ips:
            user = random.choice(self.users)
            try:
                s = HttpSession(ip)
                r = s.post("http://" + ip + "/mobile/v3/User/logIn?username=%s&password=%s&rememberme=false&appName=iphone" % (user[0], user[1]), name="http://" + ip + "/mobile/v3/User/logIn")
                if r.status_code != 200:
                    print("Status " + str(r.status_code))
                self.user_sessions[ip] = s 
                time.sleep(0.3)
            except Exception as e:
                # print(e)
                pass


    def load_products_from_active_campaign(self):
        # Get first 10 products from each of first 5 active campaigns
        r = self.client.get('http://www.morhipo.com/mobile/v3/product/activecampaignlist?imgver=MV', name='/activecampaignlist?imgver=MV')
        json_data = json.loads(r.text)
        active_campaign_list = json_data["Result"]["ActiveCampaignList"]

        for x in range(0, 5):
            try:
                campaign_id = active_campaign_list[x]["CampaignID"]
                # print(campaign_id)
                ps_product_list = self.client.get('http://www.morhipo.com/mobile/v3/product/campaignproductlist?campaignId=%s' %(str(campaign_id)), name='/mobile/v3/Product/CampaignProductList?campaignId=%s' %(str(campaign_id)))
                json_data = json.loads(ps_product_list.text)
                campaign_product_list = json_data["Result"]["ProductList"]
            except KeyError as e:
                # print(e)
                pass
            for n in range(0, 10):
                self.ps_active_campaign_product_list.append(campaign_product_list[n]["ProductPath"])


    def on_start(self):
        # we will get the target machines from Locust variable '--host' as string
        # we should set the class variable 'target_machine_ips' by host at beginning of the test
        self.target_machine_ips = str(self.parent.host).strip().split(",")

        # print("ON_START running")
        # set the lists of links by www.morhipo.com
        self.sezon_links        = self.get_urls("http://www.morhipo.com", "a", "href")
        self.ps_links           = self.get_urls("http://www.morhipo.com/kampanya/alisveris", "a", "href")
        self.kadin_links        = self.get_urls("http://www.morhipo.com/kadin/3/vitrin", "a", "href")
        self.erkek_links        = self.get_urls("http://www.morhipo.com/erkek/2/vitrin", "a", "href")
        self.ayakkabi_links     = self.get_urls("http://www.morhipo.com/ayakkabi-canta/315/vitrin", "a", "href")
        self.spor_links         = self.get_urls("http://www.morhipo.com/spor-giyim/503/vitrin", "a", "href")
        self.cocuk_links        = self.get_urls("http://www.morhipo.com/cocuk/4/vitrin", "a", "href")
        self.ev_links           = self.get_urls("http://www.morhipo.com/ev-yasam/5/vitrin", "a", "href")
        self.kozmetik_links     = self.get_urls("http://www.morhipo.com/kozmetik/235/vitrin", "a", "href")
        self.markalar_links     = self.get_urls("http://www.morhipo.com/markalar/0/marka", "a", "href")
        self.sezon_urun_detay   = self.get_urls("http://www.morhipo.com/kadin-giyim/9/liste", "#products > li > div > a", "href")

        self.load_products_from_active_campaign()
        self.load_user_sessions()


    @task(10)
    def get_login_required_pages(self):
        # get login required services
        ip = random.choice(self.target_machine_ips)
        session = self.user_sessions[ip]
        service = random.choice(self.services)
        url = "http://" + ip + service
        r = session.get(url, name=url)
        if r.status_code != 200:
            print("Status " + str(r.status_code))
            # print(url)


    @task(5)
    def test_sezon_urun_detay_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.sezon_urun_detay)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_mobile_active_campaign_list(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + "/mobile/v3/product/activecampaignlist?imgver=MV"
            self.client.get(url, name=url)
        except IndexError:
            pass


    @task(5)
    def test_ps_urun_detay_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.ps_active_campaign_product_list)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.sezon_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_ps_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.ps_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_kadin_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.kadin_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_erkek_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.erkek_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_ayakkabi_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.ayakkabi_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_spor_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.spor_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_cocuk_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.cocuk_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_sezon_ev_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.ev_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass

    @task(5)
    def test_sezon_kozmetik_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.kozmetik_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass

    @task(5)
    def test_sezon_markalar_links(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(self.markalar_links)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass


    @task(5)
    def test_ps_and_season(self):
        # this is a task to run performance testing
        # we will send http request the url taken from en çok satanlar on erkek page
        link = ["/", "/kampanya/alisveris"]
        try:
            ip = random.choice(self.target_machine_ips)
            url = "http://" + ip + random.choice(link)
            self.client.get(url, headers = { "User-Agent": self.user_agent}, name=url)
        except IndexError:
            pass

            
class User(HttpLocust):
    # will be used, just to be safe if no --host given
    host = "http://preprod.morhipo.com"

    #stop_timeout = 300

    task_set = UserBehaviour
    # time for user behaviour
    # we can assume that they wait 0.5 to 6 seconds on a page
    min_wait = 200
    max_wait = 500
