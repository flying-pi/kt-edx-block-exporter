import inspect

import os
from collections import namedtuple
from importlib import  import_module

from xblock.fields import UserScope, Sentinel

from contentstore.views.helpers import usage_key_with_run
from xmodule.modulestore.django import modulestore

import numpy as np

import modulefinder

XBlockInfo = namedtuple("XBlockInfo", ['fields', 'xblock_class', 'instance_object'])
XBlockField = namedtuple("XBlockField", ['name', 'class_name', 'serializer', 'str_value', 'is_save_value'])


class XBlockDecomposer(object):
    def __init__(self, block_usage_key_str):
        """
        :param str block_usage_key_str: string representation of the block
        """
        super(XBlockDecomposer, self).__init__()
        self.block = self._get_block_by_string_id(block_usage_key_str)

    @staticmethod
    def _get_block_by_string_id(block_usage_key_str):
        block_key = usage_key_with_run(block_usage_key_str)
        store = modulestore()
        return store.get_item(block_key)

    def _get_fields_info(self, module):
        fields = []
        for name, value in module.fields.items():
            if isinstance(value.scope, Sentinel):
                continue
            field_info = {
                'name': value.name,
                'class_name': '.'.join([value.__class__.__module__, value.__class__.__name__]),
                'serializer': 'json', 'str_value': None, 'is_save_value': False
            }

            if value.scope.user == UserScope.NONE:
                field_info['str_value'] = module.fields['name'].to_json(getattr(self.block, name))
                field_info['is_save_value'] = True

            fields.append(XBlockField(**field_info))
        return fields

    @staticmethod
    def _root_module_name(module_path):
        return module_path.split('.')[0]

    @staticmethod
    def _is_system_name(attr_name):
        """

        :param str attr_name :
        :return:
        """
        return not (attr_name.startswith("__") and attr_name.startswith("__"))

    @staticmethod
    def _get_recursive_root_path_dep(module_obj):
        result = set()
        try:
            for member_name in dir(module_obj):
                member = getattr(module_obj, member_name)
                if inspect.ismodule(member):
                    result.add(XBlockDecomposer._root_module_name(member.__name__))
                    result.update(XBlockDecomposer._get_recursive_root_path_dep(member))
        #             TODO do something with circle imports
        except:

            import pydevd_pycharm
            pydevd_pycharm.settrace('host.docker.internal', port=3758, stdoutToServer=True, stderrToServer=True)
            print('asasasasas')
        return result

    def _get_relative_pathes(self, module):
        package_to_discover = {self._root_module_name(module.__module__)}
        module_path_mapping = {}
        while package_to_discover:
            module_name = package_to_discover.pop()
            while module_name in module_path_mapping:
                module_name = package_to_discover.pop()
            imported_module = import_module(module_name)
            module_path_mapping[module_name] = '/'.join(os.path.abspath(imported_module.__file__).split('/')[:-1])+'/'
            package_to_discover.update(self._get_recursive_root_path_dep(imported_module))


            import pydevd_pycharm
            pydevd_pycharm.settrace('host.docker.internal', port=3758, stdoutToServer=True, stderrToServer=True)
            print('asasasasas')




    def get_xblock_info(self):
        module = self.block.unmixed_class
        fields = self._get_fields_info(module)
        dep_file_pathes = self._get_relative_pathes(module)



"""
import sys, traceback
try:
    
    self._get_recursive_root_path_dep(imported_module)
    
except:
    traceback.print_exc(file=sys.stdout)


"""