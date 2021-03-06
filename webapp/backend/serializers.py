#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serializers file for django rest framework.

@author: e-science Dev-team
"""

from rest_framework import serializers
from backend.models import UserInfo, ClusterInfo, ClusterCreationParams, OrkaStatistics, \
PublicNewsItem, FaqItem, FaqItemCategory, OrkaImage, OrkaImageCategory, VreServer, VreImage, VreImageCategory, Dsl, Setting


class PGArrayField(serializers.WritableField):
    """
    Override from_native and to_native methods for custom serializer
    fields for ClusterCreationParams model.
    """
    def from_native(self, data):
        if isinstance(data, list):
            return data

    def to_native(self, obj):
        return obj
      
      
class SettingsSerializer(serializers.ModelSerializer):
    """
    Serializer for Settings
    """
    class Meta:
        model = Setting
        fields = ('id', 'section', 'property_name', 'property_value', 'comment')

class VreImagesSerializer(serializers.ModelSerializer):
    """
    Serializer for VreImages metadata
    """
    image_init_extra = PGArrayField(required=False)
    image_access_url = PGArrayField(required=False)
    image_category = serializers.SerializerMethodField("category_name")
    class Meta:
        model = VreImage
        fields = ('id', 'image_name', 'image_pithos_uuid', 'image_components', 'image_min_reqs', 'image_faq_links', 'image_init_extra', 'image_access_url', 'image_category')
    
    def category_name(self,obj):
        return VreImageCategory.objects.all().filter(id=obj.image_category_id).values()[0]['category_name']

class OrkaImagesSerializer(serializers.ModelSerializer):
    """
    Serializer for OrkaImages metadata
    """
    image_init_extra = PGArrayField(required=False)
    image_access_url = PGArrayField(required=False)
    image_category = serializers.SerializerMethodField("category_name")
    class Meta:
        model = OrkaImage
        fields = ('id', 'image_name', 'image_pithos_uuid', 'image_components', 'image_min_reqs', 'image_faq_links', 'image_init_extra', 'image_access_url', 'image_category')
    
    def category_name(self,obj):
        return OrkaImageCategory.objects.all().filter(id=obj.image_category_id).values()[0]['category_name']

class NewsSerializer(serializers.ModelSerializer):
    """
    Serializer for news
    """   
    class Meta:
        model = PublicNewsItem
        fields = ('id', 'news_date', 'news_message', 'news_category')

class FaqSerializer(serializers.ModelSerializer):
    """
    Serializer for Faqs
    """
    faq_category = serializers.SerializerMethodField("category_name")
    class Meta:
        model = FaqItem
        fields = ('id', 'faq_date', 'faq_question', 'faq_answer', 'faq_category')
        
    def category_name(self,obj): # not a mandatory field, take into account null
        exists = FaqItemCategory.objects.all().filter(id=obj.faq_category_id).first() is not None
        return FaqItemCategory.objects.all().filter(id=obj.faq_category_id).values()[0]['category_name'] if exists else ''

class StatisticsSerializer(serializers.ModelSerializer):
    """
    Serializer for spawned and active clusters
    """
    id = serializers.SerializerMethodField('get_ember_id')
    
    class Meta:
        model = OrkaStatistics
        fields = ('id','spawned_clusters', 'active_clusters', 'spawned_vres', 'active_vres')
    
    def get_ember_id(self, obj):
        """"Always returns id 1 for ember.js"""
        return 1


class HdfsSerializer(serializers.Serializer):
    """
    Serializer for put files in hdfs from ftp-http
    """
    id = serializers.CharField()
    source = serializers.CharField()
    dest = serializers.CharField()
    user = serializers.CharField(required=False)
    password = serializers.CharField(required=False)


class ClusterCreationParamsSerializer(serializers.ModelSerializer):
    """
    Serializer for ClusterCreationParams model.
    Custom fields are cpu_choices, ram_choices, vms_av, disk_choices,
    disk_template and os_choices. They are custom because their model
    counterparts are arrays.
    """
    cpu_choices = PGArrayField(required=False)
    ram_choices = PGArrayField(required=False)
    vms_av = PGArrayField(required=False)
    disk_choices = PGArrayField(required=False)
    disk_template = PGArrayField(required=False)
    os_choices = PGArrayField(required=False)
    ssh_keys_names = PGArrayField(required=False)
    
    class Meta:
        model = ClusterCreationParams
        fields = ('id', 'user_id', 'project_name', 'vms_max', 'vms_av',
                  'cpu_max', 'cpu_av', 'net_av', 'floatip_av', 'ram_max', 'ram_av', 
                  'disk_max', 'disk_av', 'cpu_choices', 'ram_choices', 'disk_choices',
                  'disk_template', 'os_choices', 'ssh_keys_names')


class OkeanosTokenSerializer(serializers.Serializer):
    """Serializer for okeanos token from ember login."""
    token = serializers.CharField()


class TaskSerializer(serializers.Serializer):
    """Serializer for the celery task id."""
    task_id = serializers.CharField()


class DeleteClusterSerializer(serializers.Serializer):
    """ Serializer for master vm ip """
    master_IP = serializers.CharField(required=False)
    id = serializers.IntegerField()


class ClusterchoicesSerializer(serializers.Serializer):
    """
    Serializer for ember request with user's
    choices for cluster creation.
    """
    cluster_name = serializers.CharField(required=False)
    
    server_name = serializers.CharField(required=False)

    id = serializers.CharField(required=False)

    cluster_size = serializers.IntegerField(required=False)
    
    cpu = serializers.IntegerField(required=False)

    ram = serializers.IntegerField(required=False)

    disk = serializers.IntegerField(required=False)

    cpu_master = serializers.IntegerField(required=False)

    ram_master = serializers.IntegerField(required=False)

    disk_master = serializers.IntegerField(required=False)

    cpu_slaves = serializers.IntegerField(required=False)

    ram_slaves = serializers.IntegerField(required=False)

    disk_slaves = serializers.IntegerField(required=False)

    disk_template = serializers.CharField(required=False)

    os_choice = serializers.CharField(required=False)

    project_name = serializers.CharField(required=False)
    
    ssh_key_selection = serializers.CharField(required=False)
    
    replication_factor = serializers.CharField(required=False)
    
    dfs_blocksize = serializers.CharField(required=False)

    task_id = serializers.CharField(required=False)
    
    hadoop_status = serializers.CharField(required=False)
    
    admin_password = serializers.CharField(required=False)
    
    admin_email = serializers.CharField(required=False)
    
    cluster_edit = serializers.IntegerField(required=False)


class ClusterInfoSerializer(serializers.ModelSerializer):
    """ Serializer for ember request with user's available clusters."""
    class Meta:
        model = ClusterInfo
        fields = ('id', 'cluster_name', 'action_date', 'cluster_status', 'cluster_size',
                   'cpu_master', 'ram_master', 'disk_master', 'cpu_slaves',
                   'ram_slaves', 'disk_slaves', 'disk_template', 'os_image',
                   'master_IP', 'project_name', 'replication_factor', 'dfs_blocksize', 'task_id', 'state', 'hadoop_status')

       
class VreServerSerializer(serializers.ModelSerializer):
    """ Serializer for VRE server model."""
    class Meta:
        model = VreServer
        fields = ('id', 'server_name', 'action_date', 'server_status','cpu', 'ram', 'disk', 'disk_template',
                  'os_image','server_IP', 'project_name', 'task_id', 'state')


class DslsSerializer(serializers.ModelSerializer):
    """
    Serializer for getting User Reproducible Experiments DSL metadata
    """   
    class Meta:
        model = Dsl
        fields = ('id', 'dsl_name', 'action_date', 'dsl_status', 'pithos_path', 'cluster_id', 'task_id', 'state', 'dsl_data')

class DslOptionsSerializer(serializers.Serializer):
    """
    Serializer for submitting Reproducible Experiments DSL options
    """
    dsl_name = serializers.CharField(required=True)
    pithos_path = serializers.CharField(required=True)
    cluster_id = serializers.IntegerField(required=False)
    
class DslDeleteSerializer(serializers.Serializer):
    """
    Serializer for submitting Reproducible Experiment metadata delete request
    """
    id = serializers.IntegerField()

class UserInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for UserInfo object with cluster and escience_token
    added fields.
    """
    cluster = serializers.SerializerMethodField('number_of_clusters')
    vrenum = serializers.SerializerMethodField('number_of_vres')
    dslnum = serializers.SerializerMethodField('number_of_dsls')
    escience_token = serializers.RelatedField()
    id = serializers.SerializerMethodField('get_ember_id')
    clusters = ClusterInfoSerializer(many=True)
    vreservers = VreServerSerializer(many=True)
    dsls = DslsSerializer(many=True)

    class Meta:
        model = UserInfo
        fields = ('id', 'user_id', 'user_name', 'user_theme', 'cluster', 'vrenum', 'dslnum', 'master_vm_password', 'error_message',
                  'escience_token', 'clusters', 'vreservers', 'dsls')

    def number_of_clusters(self, obj):
        """
        Function that calculates the number of clusters of a UserInfo instance.
        """
        clusters = ClusterInfo.objects.all().filter(user_id=obj.user_id). \
            filter(cluster_status=1).count()
        return clusters
    
    def number_of_vres(self, obj):
        """
        Function that calculates the number of active VREs of a UserInfo instance.
        """
        vres = VreServer.objects.all().filter(user_id=obj.user_id). \
            filter(server_status=1).count()
        return vres
    
    def number_of_dsls(self, obj):
        """
        Function that returns the number of DSLs in a UserInfo instance.
        """
        dsls = Dsl.objects.all().filter(user_id=obj.user_id).count()
        return dsls

    def get_ember_id(self, obj):
        """"Always returns id 1 for ember.js"""
        return 1


class UserPutSerializer(serializers.Serializer):
    """
    Serializer for ember request with user's
    choices for theme or error_message update.
    """
    user_theme = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)