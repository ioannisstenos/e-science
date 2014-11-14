#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Selenium test for the disk_size limit error message in summary screen

@author: Ioannis Stenos, Nick Vrionis
'''

from selenium import webdriver
import sys
from os.path import join, dirname, abspath
sys.path.append(join(dirname(abspath(__file__)), '../..'))
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import unittest, time, re
from okeanos_utils import check_quota, get_flavor_id, destroy_cluster
from create_bare_cluster import create_cluster
from ClusterTest import ClusterTest


class TestClusterDiskSize(ClusterTest):
    '''Test Class for the disk_size limit error message'''
    def test_cluster(self):

        driver = self.login()
        # Get user quota from kamaki
        user_quota = check_quota(self.token)
        flavors = get_flavor_id(self.token)
        # List of disk size choices
        disk_list = flavors['disk']
        # Avalable user disk size
        available_disk = user_quota['disk']['available']
        cluster_size, master, slave ,remaining_disk = self.calculate_cluster_resources(disk_list, available_disk)
        # Give Selenium the values cluster_size, master and slave to use for
        # the cluster_size and disk size buttons of cluster/create screen.
        driver.find_element_by_id("master").click()
        Select(driver.find_element_by_id("size_of_cluster")).select_by_visible_text(str(cluster_size))
        time.sleep(1)
        try:
            master_ip, server = self.bind_okeanos_resources(remaining_disk, disk_list)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[1]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[3]/button["+ master +"]").click()
            time.sleep(1)
            driver.find_element_by_id("slaves").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[1]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[2]/button").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/p[3]/button["+ slave +"]").click()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/h4[5]/input").clear()
            time.sleep(1)
            driver.find_element_by_xpath("//div[@id='content-wrap']/h4[5]/input").send_keys("mycluster")
            time.sleep(1)
            driver.find_element_by_id("next").click()
            driver.find_element_by_id("next").click()
            for i in range(60):
                try:
                    if "Disk size selection exceeded cyclades disk size limit" == driver.find_element_by_css_selector("#footer > h4").text: break
                except: pass
                time.sleep(1)
            else: self.fail("time out")
            time.sleep(3)
            self.assertEqual("Disk size selection exceeded cyclades disk size limit",
                             driver.find_element_by_css_selector("#footer > h4").text)
        finally:
            cluster_name = server[0]['name'].rsplit('-', 1)[0]
            destroy_cluster(cluster_name, self.token)

    def bind_okeanos_resources(self, remaining_disk, disk_list):
        '''
        Create a bare cluster in ~okeanos with two vms. The disk size depend
        on remaining_disk argument.
        '''
        if remaining_disk == 0:
            return create_cluster(name=self.name,
                                  clustersize=2,
                                  cpu_master=1, ram_master=1024, disk_master=5,
                                  disk_template='ext_vlmc', cpu_slave=1,
                                  ram_slave=1024, disk_slave=5,
                                  token=self.token, image='Debian Base')
        else:
            for disk in disk_list:
                if disk >= remaining_disk:
                    remaining_disk = disk
                    return create_cluster(name=self.name,
                                          clustersize=2,
                                          cpu_master=1, ram_master=1024,
                                          disk_master=remaining_disk,
                                          disk_template='ext_vlmc',
                                          cpu_slave=1, ram_slave=1024,
                                          disk_slave=remaining_disk,
                                          token=self.token,
                                          image='Debian Base')

if __name__ == "__main__":
    unittest.main()