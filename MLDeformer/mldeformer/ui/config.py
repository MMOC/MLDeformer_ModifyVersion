# -*- coding: utf-8 -*-
# Copyright Epic Games, Inc. All Rights Reserved

import json
import os

from .json_encoder import JsonEncoder
from .mesh_mapping import MeshMapping
from .parameter import Parameter


# The configuration and parameters state.
# This is like the state of the system, after a user configures it.
# Those settings can be saved and loaded to/from json files.
class Config:
    def __init__(self, output_folder):
        self.config_version = 2
        self.num_samples = 50000
        self.start_frame = 0
        self.random_seed = 7777
        self.controller_probability = 0.2
        self.save_target_alembic = True
        self.output_fbx_file = os.path.join(output_folder, 'BaseMesh.Fbx')
        self.output_abc_file = os.path.join(output_folder, 'TargetMesh.Abc')
        self.parameters = list()
        self.mesh_mappings = list()
        # Modify
        self.Visibility = 1

    def has_parameter(self, param_name):
        for param in self.parameters:
            if param.name == param_name:
                return True
        return False

    # Init the class members from already parsed json data.
    def init_from_json_data(self, config_data):
        if 'num_samples' in config_data: self.num_samples = config_data['num_samples']
        if 'start_frame' in config_data: self.start_frame = config_data['start_frame']
        if 'random_seed' in config_data: self.random_seed = config_data['random_seed']
        if 'controller_probability' in config_data: self.controller_probability = config_data['controller_probability']

        if 'output_fbx_file' in config_data: self.output_fbx_file = config_data['output_fbx_file']
        if 'output_abc_file' in config_data: self.output_abc_file = config_data['output_abc_file']

        if 'save_target_alembic' in config_data: self.save_target_alembic = config_data['save_target_alembic']
        # Modify
        if 'Visibility' in config_data: self.Visibility = config_data['Visibility']

        # Read the mesh mappings.
        del self.mesh_mappings[:]
        if 'mesh_mappings' in config_data:
            for mapping in config_data['mesh_mappings']:
                base_mesh = mapping['base_mesh_name'] if 'base_mesh_name' in mapping else ''
                target_mesh = mapping['target_mesh_name'] if 'target_mesh_name' in mapping else ''
                enabled = mapping['is_enabled'] if 'is_enabled' in mapping else True
                new_mapping = MeshMapping(base_mesh, target_mesh, enabled)
                self.mesh_mappings.append(new_mapping)
        else:
            base_mesh_name = ''
            target_mesh_name = ''
            if 'base_mesh_name' in config_data: base_mesh_name = config_data['base_mesh_name']
            if 'target_mesh_name' in config_data: target_mesh_name = config_data['target_mesh_name']
            if base_mesh_name and target_mesh_name:
                new_mapping = MeshMapping(base_mesh_name, target_mesh_name, enabled=True)
                self.mesh_mappings.append(new_mapping)

        if self.mesh_mappings:
            self.mesh_mappings.sort(key=lambda x: x.base_mesh_name.lower())

        # Init the parameters.
        del self.parameters[:]
        for parameter_data in config_data['parameters']:
            
            if not all(item in parameter_data for item in ['name', 'display_name', 'default_value', 'min_value', 'max_value', 'object_type']):
                continue
            new_parameter = Parameter()
            if 'name' in parameter_data: new_parameter.name = parameter_data['name']
            if 'display_name' in parameter_data: new_parameter.display_name = parameter_data['display_name']
            if 'default_value' in parameter_data: new_parameter.default_value = parameter_data['default_value']
            if 'min_value' in parameter_data: new_parameter.min_value = parameter_data['min_value']
            if 'max_value' in parameter_data: new_parameter.max_value = parameter_data['max_value']
            if 'object_type' in parameter_data: new_parameter.object_type = parameter_data['object_type']
            if 'group_name' in parameter_data: new_parameter.group_name = parameter_data['group_name']

            self.parameters.append(new_parameter)

        if len(self.parameters) > 0:
            self.parameters.sort(key=lambda x: x.display_name.lower())

    def save_to_file(self, file_path):
        json_string = json.dumps(self, sort_keys=True, indent=4, cls=JsonEncoder)
        with open(file_path, 'wt') as writeFile:
            writeFile.writelines(json_string)

    def load_from_file(self, file_path):
        json_string = ''
        with open(file_path, 'rt') as readFile:
            json_string = readFile.readlines()
            if len(json_string) > 0:
                json_string = ' '.join(json_string)  # Turn the list of strings into one string.
                data = json.loads(json_string)
                self.init_from_json_data(data)
