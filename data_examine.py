#!/usr/bin/python
# -*- coding: utf-8 -*-

# Shanghai Tongji Urban Planning & Design Institute Co., Ltd. - Academy of Spatial Planning
# zongli@tjupdi.com
# Composed in Python 3.6.10 for ArcGIS Pro

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import arcpy
import csv
import json
import codecs
import sys
import time
from math import isnan

def get_data(work_space_path):
    arcpy.env.workspace = work_space_path
    return arcpy.ListFeatureClasses() + arcpy.ListRasters()

def get_rasters(work_space_path):
    arcpy.env.workspace = work_space_path
    return arcpy.ListRasters()

def get_featureclasses(work_space_path):
    arcpy.env.workspace = work_space_path
    return arcpy.ListFeatureClasses()

def get_datasets(work_space_path):
    arcpy.env.workspace = work_space_path
    return arcpy.ListDatasets()

def get_tables(work_space_path):
    arcpy.env.workspace = work_space_path
    return arcpy.ListTables()

def get_workspaces(work_space_path, wild_card = "*", workspace_type = "All"):
    arcpy.env.workspace = work_space_path
    return arcpy.ListWorkspaces(wild_card, workspace_type)

def get_target_gdb(dir_path):
    o_workspaces = get_workspaces(dir_path, "*", "FileGDB")
    p_workspaces = []
    for workspace in o_workspaces:
        if not workspace.endswith("_flat.gdb"):
            p_workspaces.append(workspace)
    p_workspace = ""
    if len(p_workspaces) > 1:
        print("当前路径下存在多个数据库：")
        for workspace in p_workspaces:
            print(workspace.split("\\")[-1])
        print(">>>")
        while p_workspace == '':
            print("请输入目标数据库名称：")
            input_db_name = input()
            for workspace in p_workspaces:
                if input_db_name in workspace:
                    p_workspace = workspace
        return p_workspace
    elif len(p_workspaces) == 1:
        p_workspace = p_workspaces[0]
        return p_workspace
    else:
        sys.exit("当前路径下无数据库！程序退出。")

def get_target_fc(work_space_path, fc_name = "", fc_name_list = []):
    if fc_name == "" and fc_name_list != []:
        fc_list = conduct_featureclass_list(work_space_path)
        p_fc = ''
        for fc in fc_name_list:
            for r_fc in fc_list:
                if r_fc.split("\\")[-1] == fc:
                    p_fc = r_fc
                    break
            if p_fc != "":
                break
        if p_fc != '':
            return p_fc
        else:
            p_fc = get_target_fc_by_name(work_space_path, fc_name)
            return p_fc
    else:
        p_fc = get_target_fc_by_name(work_space_path, fc_name)
        return p_fc

def get_target_fc_by_name(work_space_path, fc_name):
    fc_list = conduct_featureclass_list(work_space_path)
    n_fc_list = []
    for p_fc in fc_list:
        if fc_name in p_fc:
            n_fc_list.append(p_fc)
    p_fc = ''
    if len(n_fc_list) > 1:
        print("当前路径下存在多个符合名称要求的要素集：")
        for fc in n_fc_list:
            print(fc.split("\\")[-1])
        print(">>>")
        while p_fc == '':
            print("请输入目标数据集名称：")
            input_fc_name = input()
            for fc in n_fc_list:
                if input_fc_name in fc:
                    p_fc = fc
        return p_fc
    elif len(n_fc_list) == 1:
        return n_fc_list[0]
    else:
        print(">>>")
        while p_fc == '':
            print("当前路径下不存在符合名称要求的要素集，请重新输入名称：")
            input_fc_name = input()
            n_fc_list = conduct_featureclass_list(work_space_path)
            for fc in n_fc_list:
                if input_fc_name in fc:
                    p_fc = fc
        return p_fc

def get_target_data_from_list(work_space_path, data_list, fc_name = "", fc_name_list = []):
    target_data = ""
    if fc_name == "" and fc_name_list != []:
        for p_fc_name in fc_name_list:
            for data in data_list:
                if data.split("\\")[-1] == p_fc_name:
                    target_data = data
    else:
        for data in data_list:
            if data.split("\\")[-1] == fc_name:
                target_data = data
    if target_data != "":
        return target_data
    else:
        return get_target_fc_by_name(work_space_path, fc_name)

def get_structure_info(dir_path, ds_file_name=''):
    if ds_file_name == "":
        ds_file_path = dir_path + "\\" + "data_structure.csv"
    else:
        ds_file_path = dir_path + "\\" + ds_file_name
    
    if not os.path.isfile(ds_file_path):
        p_structure_file_path = ""
        while p_structure_file_path == "":
            print(">>>")
            print("当前路径下不存在符合名称要求的数据结构描述文件，请重新输入名称（包括后缀）：")
            input_sf_name = input()
            ds_file_path = dir_path + "\\" + input_sf_name
            if os.path.isfile(ds_file_path):
                p_structure_file_path = ds_file_path

    p_set = set()
    with codecs.open(ds_file_path, encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file)
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            if line_count > 0:
                p_set.add(row[0])
    return p_set

def output_info(output_string, output_path = ""):
    print(output_string)
    if output_path == "":
        global output_file_path
        with codecs.open(output_file_path, 'a') as output_file:
            output_file.write(output_string + '\n')
        return 1
    else:
        with codecs.open(output_path, 'a') as output_file:
            output_file.write(output_string + '\n')
        return 0

def conduct_data_list(gdb_path):
    work_spaces = [gdb_path]
    datasets = []
    for dataset in get_datasets(gdb_path):
        datasets.append(gdb_path + "\\" + dataset)

    work_spaces += datasets

    data_list = []

    for work_space in work_spaces:
        for data in get_data(work_space):
            data_list.append(work_space + "\\" + data)

    return data_list

def conduct_featureclass_list(gdb_path):
    work_spaces = [gdb_path]
    datasets = []
    for dataset in get_datasets(gdb_path):
        datasets.append(gdb_path + "\\" + dataset)

    data_list = []
    work_spaces += datasets
    for work_space in work_spaces:
        for data in get_featureclasses(work_space):
            data_list.append(work_space + "\\" + data)

    return data_list

def conduct_table_list(gdb_path):
    work_spaces = [gdb_path]
    datasets = []
    for dataset in get_datasets(gdb_path):
        datasets.append(gdb_path + "\\" + dataset)

    data_list = []
    work_spaces += datasets
    for work_space in work_spaces:
        for data in get_tables(work_space):
            data_list.append(work_space + "\\" + data)

    return data_list

def check_reference(data_list):
    spatial_ref_name_list = []
    spatial_data_ref_list = []

    for data in data_list:
        spatial_ref = arcpy.Describe(data).spatialReference
        if not spatial_ref.name in spatial_ref_name_list:
            spatial_ref_name_list.append(spatial_ref.name)
        if arcpy.Describe(data).dataType == "RasterBand":
            pass
        else:
            spatial_data_ref_list.append([data.split("\\")[-1], spatial_ref.name])

    if len(spatial_ref_name_list) > 1:
        output_info(f"数据库中使用了 {len(spatial_ref_name_list)} 个坐标系统，具体信息为：")
        for spatial_data_ref in spatial_data_ref_list:
            if spatial_data_ref[1] == "Unknown":
                output_info("{}, Unknown".format(spatial_data_ref[0].split("\\")[-1]))
            else:
                output_info("{}, {}".format(spatial_data_ref[0].split("\\")[-1], spatial_data_ref[1]))
        return 0
    elif len(spatial_ref_name_list) == 1:
        output_info(f"数据库中坐标系统已统一为：{spatial_ref_name_list[0]}")
        return 1
    else:
        output_info(f"数据库为空或无可用坐标系统！")
        return -1

def check_geometry(featureclass_list):
    total_count, p_count = 0, 0
    fields = ['CLASS', 'FEATURE_ID', 'PROBLEM']
    for featureclass in featureclass_list:
        p_count = 0
        p_output_name = "memory\\" + featureclass.split("\\")[-1]
        arcpy.CheckGeometry_management(featureclass, p_output_name)
        p_count = int(arcpy.GetCount_management(p_output_name)[0])
        if p_count > 0:
            output_info(f"{featureclass} 存在几何错误。错误信息如下：")
            with arcpy.da.SearchCursor(p_output_name, fields) as cursor:
                for row in cursor:
                    output_info('{0}, {1}, {2}'.format(row[0], row[1], row[2]))
        else:
            print(f"{featureclass} 不存在几何错误。")
        total_count += p_count
        delete_temp(p_output_name)
    if total_count > 0:
        output_info(f"数据库中共存在有 {total_count} 个几何错误，请注意修正。")
        return 0
    else:
        output_info("数据库中不存在几何错误。")
        return 1

def check_extent(base_data, data_list):
    signal = 1
    if base_data in data_list:
        data_list.remove(base_data)
    base_data_desc = arcpy.Describe(base_data)
    if isnan(base_data_desc.extent.XMin) or isnan(base_data_desc.extent.YMin) or \
       isnan(base_data_desc.extent.XMax) or isnan(base_data_desc.extent.YMax):
        sys.exit("基准范围验证数据为空或存在范围错误！")
    
    center_point = ((base_data_desc.extent.XMax + base_data_desc.extent.XMin) / 2, \
                    (base_data_desc.extent.YMax + base_data_desc.extent.YMin) / 2)
    
    xy_range = ((base_data_desc.extent.XMax - base_data_desc.extent.XMin), \
                (base_data_desc.extent.YMax - base_data_desc.extent.YMin))

    extended_extent = (center_point[0] - xy_range[0], center_point[1] - xy_range[1], \
                       center_point[0] + xy_range[1], center_point[1] + xy_range[1])

    for data in data_list:
        if arcpy.Describe(data).dataType == "RasterBand":
            pass
        else:
            p_desc = arcpy.Describe(data)
            p_name, p_extent = p_desc.name, p_desc.extent
            if isnan(p_extent.XMin) or isnan(p_extent.YMin) or isnan(p_extent.XMax) or isnan(p_extent.YMax):
                output_info(f"{p_name} 数据为空或存在范围错误！")
                if signal > -1:
                    signal = -1
            elif p_extent.XMin < extended_extent[0] or p_extent.YMin < extended_extent[1] or \
               p_extent.XMax > extended_extent[2] or p_extent.YMax > extended_extent[3]:
                output_info(f"{p_name} 范围可能异常！")
                if signal > 0:
                    signal = 0
    if signal == 1:
        output_info("数据范围正常。")
    return signal

def check_fc_boundary(base_data, fc_list):
    signal = 1
    if base_data in fc_list:
        fc_list.remove(base_data)
    for featureclass in fc_list:
        if arcpy.Describe(featureclass).featureType != "Annotation":
            p_output_name = "memory\\" + featureclass.split("\\")[-1] + "_erase"
            arcpy.Erase_analysis(featureclass, base_data, p_output_name)
            p_count = int(arcpy.GetCount_management(p_output_name)[0])
            if p_count > 0:
                output_info(f"{featureclass} 超出规划范围，需要核对。")
                signal -= 1
            else:
                print(f"{featureclass} 未超出规划范围。")
            delete_temp(p_output_name)
    if signal == 1:
        output_info("全部数据均落入规划范围内。")
    return signal

def check_data_structure(data_list, name_set):
    signal = 1
    ir_set = set()
    for data in data_list:
        if data.split("\\")[-1] in name_set:
            print(f"{data} 命名规范。")
        else:
            output_info(f"{data} 命名不规范！")
            ir_set.add(data.split("\\")[-1])
    if ir_set:
        p_output_set_info = ", ".join(ir_set)
        output_info(f"命名不规范的图层为：{p_output_set_info}。")
        signal = 0
    else:
        output_info("所有图层皆规范命名。")
    return signal

def summarize_table_structure(data_list):
    signal = 1
    for data in data_list:
        field_list = arcpy.ListFields(data)
        if field_list and arcpy.Describe(data).dataType != "RasterBand":
            p_field_info = data.split("\\")[-1] + ","
            for field in field_list:
                if field.name in ["Shape_Area", "Shape_Length"]:
                    pass
                else:
                    if field.aliasName:
                        p_field_info += f" {field.aliasName}, {field.type}, {field.length},"
                    else:
                        p_field_info += f" {field.name}, {field.type}, {field.length},"
            p_field_info = p_field_info[:-1]
            output_info(p_field_info)
        else:
            print(f"{data} 无数据表或非数据表检测对象。")
    return signal

def export_to_flat_gdb(dir_path, gdb, data_list):
    gdb_name = gdb.split('\\')[-1].split(".")[0]
    flat_gdb_path = dir_path + "\\" + gdb_name + "_flat.gdb"
    if arcpy.Exists(flat_gdb_path):
        sys.exit("该数据库已存在！")
    else:
        arcpy.CreateFileGDB_management(dir_path, gdb_name + "_flat")
        for data in data_list:
            if arcpy.Describe(data).dataType == "RasterBand":
                pass
            else:
                arcpy.Copy_management(data, flat_gdb_path + "\\" + data.split("\\")[-1])
                print(f"{data} 导出成功。")
        return 1

def check_geometry_single(featureclass):
    p_count = 0
    fields = ['CLASS', 'FEATURE_ID', 'PROBLEM']
    p_output_name = "memory\\" + featureclass.split("\\")[-1] + "_cktb"
    arcpy.CheckGeometry_management(featureclass, p_output_name)
    p_count = int(arcpy.GetCount_management(p_output_name)[0])
    if p_count > 0:
        output_info(f"{featureclass} 存在几何错误。错误信息如下：")
        with arcpy.da.SearchCursor(p_output_name, fields) as cursor:
            for row in cursor:
                output_info('{0}, {1}, {2}'.format(row[0], row[1], row[2]))
    else:
        print(f"{featureclass} 不存在几何错误。")
    delete_temp(p_output_name)
    if p_count > 0:
        return 0
    else:
        return 1

def repair_geometry_interactive(featureclass):
    p_repair_signal = -1
    while p_repair_signal == -1:
        cm = input()
        if cm == "Y" or cm == "y":
            p_repair_signal = 1
            output_info(f"{featureclass} 将被修正。")
        else:
            p_repair_signal = 0
            output_info(f"{featureclass} 未修正。")
    if p_repair_signal == 1:
        arcpy.RepairGeometry_management(featureclass)
        return 1
    else:
        return 0

def repair_geometry(featureclass_list, dir_path):
    repair_signal_list = []
    p_temp_gdb = create_temp_gdb(dir_path)
    for featureclass in featureclass_list:
        p_signal = check_geometry_single(featureclass)
        if p_signal == 1:
            pass
        else:
            p_output_name = p_temp_gdb + "\\" + featureclass.split("\\")[-1]
            arcpy.CopyFeatures_management(featureclass, p_output_name)
            arcpy.RepairGeometry_management(p_output_name)
            if arcpy.Describe(featureclass).shapeType == "Point":
                o_count = int(arcpy.GetCount_management(featureclass)[0])
                n_count = int(arcpy.GetCount_management(p_output_name)[0])
                print(f"当前待修正要素集为 {featureclass}")
                print(f"修正前点数量为 {o_count} 个，修正后点数量为 {n_count} 个。")
                print('是否修正？是（Y），否（N or any other input）')
                repair_signal_list.append(repair_geometry_interactive(featureclass))

            elif arcpy.Describe(featureclass).shapeType == "Polyline":
                fields = ["Shape_Length"]
                # arcpy.AddField_management(p_output_name, fields[0], "DOUBLE")
                # arcpy.CalculateGeometryAttributes_management(p_output_name, \
                #     [[fields[0], "LENGTH"]], "METERS")
                o_length_count, n_length_count = 0, 0
                with arcpy.da.SearchCursor(featureclass, fields) as cursor:
                    for row in cursor:
                        o_length_count += row[0]
                with arcpy.da.SearchCursor(p_output_name, fields) as cursor:
                    for row in cursor:
                        n_length_count += row[0]
                o_count = int(arcpy.GetCount_management(featureclass)[0])
                n_count = int(arcpy.GetCount_management(p_output_name)[0])
                print(f"当前待修正要素集为 {featureclass}")
                print(f"修正前线要素数量为 {o_count} 个，修正后线要素数量为 {n_count} 个。")
                print(f"修正前线要素长度 {o_length_count}m，修正后线要素长度 {n_length_count}m。")
                print('是否修正？是（Y），否（N or any other input）')
                repair_signal_list.append(repair_geometry_interactive(featureclass))

            elif arcpy.Describe(featureclass).shapeType == "Polygon":
                fields = ["Shape_Area"]
                # arcpy.AddField_management(p_output_name, fields[0], "DOUBLE")
                # arcpy.CalculateGeometryAttributes_management(p_output_name, \
                #     [[fields[0], "AREA"]], area_unit='SQUARE_METERS')
                o_area_count, n_area_count = 0, 0
                with arcpy.da.SearchCursor(featureclass, fields) as cursor:
                    for row in cursor:
                        o_area_count += row[0]
                with arcpy.da.SearchCursor(p_output_name, fields) as cursor:
                    for row in cursor:
                        n_area_count += row[0]
                o_count = int(arcpy.GetCount_management(featureclass)[0])
                n_count = int(arcpy.GetCount_management(p_output_name)[0])
                print(f"当前待修正要素集为 {featureclass}")
                print(f"修正前面要素数量为 {o_count} 个，修正后面要素数量为 {n_count} 个。")
                print(f"修正前面要素面积为 {o_area_count}㎡，修正后面要素面积为 {n_area_count}㎡。")
                print('是否修正？是（Y），否（N or any other input）')
                repair_signal_list.append(repair_geometry_interactive(featureclass))

            elif arcpy.Describe(featureclass).shapeType == "Multipoint":
                output_info(f"{featureclass} 图形类型错误，无法修正！")

            elif arcpy.Describe(featureclass).shapeType == "MultiPatch":
                output_info(f"{featureclass} 图形类型错误，无法修正！")

            delete_temp(p_output_name)
    delete_temp(p_temp_gdb)
    return repair_signal_list

def create_temp_gdb(dir_path):
    gdb_name = "temp_" + str(int(time.time()))
    gdb_path = dir_path + "\\" + gdb_name + ".gdb"
    arcpy.CreateFileGDB_management(dir_path, gdb_name)
    return gdb_path

def delete_temp(temp_name):
    arcpy.Delete_management(temp_name)
    return 1

def check_mode(check_list):
    p_check_mode = ""
    print("请输入运行模式，全部检测（Y）或自定义（X）:")
    print(">>>\n")
    while p_check_mode == "":
        cm = input()
        if cm == "Y" or cm == "y":
            p_check_mode = "Y"
        elif cm == "X" or cm == "x":
            p_check_mode = "X"
        else:
            print("模式输入错误，请重新输入:")

    if p_check_mode == "Y":
        print("执行全部检测>>>")
        return check_list[:6]
    else:
        print(", ".join(check_list))
        print("现有检测/处理方法如上，请输入需使用的检测/处理方法名：")
        p_input = ""
        while p_input == "":
            pin = input()
            if pin in check_list:
                print(f"选定的检测/处理方法为 {pin} >>>\n")
                p_input = pin
            else:
                print("方法输入错误，请重新输入:")
        n_check_dict = [p_input]
    return n_check_dict

def process_main(func_name, para_dict):
    if func_name == "坐标系统":
        output_info("\n坐标系统检测结果：")
        p_signal = check_reference(para_dict['data_list'])
        if p_signal == -1:
                sys.exit("数据库错误，退出检测！")
        return p_signal
    elif func_name == "几何":
        output_info("\n几何检测结果：")
        p_signal = check_geometry(para_dict['featureclass_list'])
        return p_signal
    elif func_name == '数据范围':
        output_info("\n数据范围检测结果：")
        p_signal = check_extent(para_dict['region_fc'], para_dict['data_list'])
        return p_signal
    elif func_name == '规划范围':
        output_info("\n规划范围检测结果：")
        p_signal = check_fc_boundary(para_dict['region_fc'], para_dict['featureclass_list'])
        return p_signal
    elif func_name == '数据结构':
        output_info("\n数据结构检测结果：")
        p_structure_info = get_structure_info(para_dict['dir'], para_dict['strcuture_file_name'])
        p_signal = check_data_structure(para_dict['data_list'], p_structure_info)
        return p_signal
    elif func_name == '数据表结构':
        output_info("\n数据表结构：")
        p_signal = summarize_table_structure(para_dict['data_list'])
        return p_signal
    elif func_name == '去除数据层级':
        output_info("\n新建无 dataset 数据库：")
        export_to_flat_gdb(para_dict['dir'], para_dict['gdb'], para_dict['data_list'])
        sys.exit("新建无 dataset 数据完成，程序退出...")
    elif func_name == '几何修正':
        p_signal = repair_geometry(para_dict['featureclass_list'], para_dict['dir'])
        return p_signal
    else:
        sys.exit("函数错误，退出检测！")

if __name__ == "__main__":

    check_list = ["坐标系统", "几何", "数据范围", "规划范围", "数据结构", \
                "数据表结构", "去除数据层级", "几何修正"]
    admin_fc_name_list = ["行政区划_市级", "行政区划_县级", "行政区划_乡级", "行政区划_村级"]
    structure_file_name = ""
    admin_fc_name = ''
    check_signal = []

    dir_path = os.path.dirname(os.path.realpath(__file__))
    p_gdb = get_target_gdb(dir_path)
    output_file_path = dir_path + "\\" + p_gdb.split("\\")[-1].split(".")[-2] + ".csv"
    p_data_list = conduct_data_list(p_gdb)
    p_featureclass_list = conduct_featureclass_list(p_gdb)

    print("初始化完成>>>\n")
    output_info(f"被检测数据库为：{p_gdb}\n")
    print("获取规划区划范围要素>>>\n")

    p_region_fc = get_target_fc(p_gdb, "", admin_fc_name_list)
    para_dict = {'dir': dir_path,'gdb': p_gdb, 'data_list': p_data_list, 'featureclass_list': p_featureclass_list, \
        'region_fc': p_region_fc, 'admin_fc_name': admin_fc_name, 'admin_fc_name_list': admin_fc_name_list, \
        'strcuture_file_name': structure_file_name}
    p_check_mode = check_mode(check_list)

    print("开始检测>>>\n")

    for check in p_check_mode:
        check_signal.append(process_main(check, para_dict))

    output_info(f"\n检测/处理结束，状态：{check_signal}。")


    #tbd: topology check: No overlapping, No intersection
    #tbd: conversion to provincial standard database
    #tbd: extract key indicators and ratios