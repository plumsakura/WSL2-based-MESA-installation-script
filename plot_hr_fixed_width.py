#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
处理MESA固定宽度格式的history.data文件
"""

import numpy as np
import matplotlib.pyplot as plt
import os

def read_mesa_fixed_width(file_path):
    """
    读取固定宽度格式的MESA history.data文件
    """
    print(f"正在读取文件: {file_path}")
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在: {file_path}")
        return None
    
    # 读取所有行
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    print(f"文件总行数: {len(lines)}")
    
    # 找到包含'model_number'的行（标题行）
    title_line_num = -1
    for i, line in enumerate(lines):
        if 'model_number' in line:
            title_line_num = i
            break
    
    if title_line_num == -1:
        print("错误：找不到标题行（包含'model_number'）")
        return None
    
    print(f"标题行在第 {title_line_num + 1} 行")
    
    # 提取列名（去掉多余的空格）
    header_line = lines[title_line_num].strip()
    column_names = header_line.split()
    print(f"找到 {len(column_names)} 个列名")
    
    # 从标题行的下一行开始读取数据
    data_lines = lines[title_line_num + 1:]
    print(f"数据行数: {len(data_lines)}")
    
    # 解析数据
    data = []
    for i, line in enumerate(data_lines):
        line = line.strip()
        if not line:  # 跳过空行
            continue
        
        # 按空格分割，转换为浮点数
        parts = line.split()
        try:
            values = [float(x) for x in parts]
            if len(values) == len(column_names):
                data.append(values)
        except ValueError:
            print(f"警告：第{i+1}行解析失败: {line[:50]}...")
    
    if not data:
        print("错误：没有有效数据")
        return None
    
    data_array = np.array(data)
    print(f"有效数据行数: {len(data)}")
    print(f"数据形状: {data_array.shape}")
    
    # 创建数据字典
    data_dict = {}
    for i, col_name in enumerate(column_names):
        data_dict[col_name] = data_array[:, i]
    
    # 检查关键列是否存在
    print("\n检查关键列:")
    for col in ['model_number', 'star_age', 'log_Teff', 'log_L']:
        if col in data_dict:
            print(f"  ✓ {col}: 存在")
        else:
            print(f"  ✗ {col}: 缺失")
    
    return data_dict, column_names

def plot_simple_hr_diagram(data_dict):
    """
    绘制简单的赫罗图
    """
    # 检查必要的列
    required_cols = ['log_Teff', 'log_L', 'star_age']
    for col in required_cols:
        if col not in data_dict:
            print(f"错误：缺少必要的列: {col}")
            print(f"可用的列: {list(data_dict.keys())}")
            return None
    
    # 提取数据
    log_teff = data_dict['log_Teff']
    log_L = data_dict['log_L']
    age = data_dict['star_age']
    
    print(f"\n数据范围:")
    print(f"  log_Teff: {min(log_teff):.3f} 到 {max(log_teff):.3f}")
    print(f"  log_L: {min(log_L):.3f} 到 {max(log_L):.3f}")
    print(f"  年龄: {min(age):.2e} 到 {max(age):.2e} 年")
    
    # 创建赫罗图
    plt.figure(figsize=(10, 8))
    
    # 绘制散点图，颜色表示年龄
    scatter = plt.scatter(log_teff, log_L, 
                         c=age, 
                         cmap='viridis',
                         s=30, 
                         alpha=0.8,
                         edgecolor='k',
                         linewidth=0.5)
    
    # 反转x轴（温度越高越靠左）
    plt.gca().invert_xaxis()
    
    # 设置标签
    plt.xlabel(r'$\log_{10}(T_{\mathrm{eff}}/\mathrm{K})$', fontsize=14)
    plt.ylabel(r'$\log_{10}(L/L_{\odot})$', fontsize=14)
    plt.title('1倍太阳质量恒星演化轨迹', fontsize=16, fontweight='bold')
    
    # 添加颜色条
    cbar = plt.colorbar(scatter)
    cbar.set_label('恒星年龄 (年)', fontsize=12)
    
    # 添加网格
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # 调整布局
    plt.tight_layout()
    
    # 保存图片
    plt.savefig('hr_diagram_1Msun.png', dpi=300, bbox_inches='tight')
    print("图片已保存为 'hr_diagram_1Msun.png'")
    
    plt.show()
    
    return True

def plot_multiple_plots(data_dict):
    """
    绘制多个子图
    """
    if not all(col in data_dict for col in ['log_Teff', 'log_L', 'star_age']):
        return
    
    log_teff = data_dict['log_Teff']
    log_L = data_dict['log_L']
    age = data_dict['star_age']
    
    # 创建2x2的子图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # 图1：赫罗图
    ax1 = axes[0, 0]
    scatter1 = ax1.scatter(log_teff, log_L, c=age, cmap='viridis', s=20)
    ax1.invert_xaxis()
    ax1.set_xlabel(r'$\log_{10}(T_{\mathrm{eff}}/\mathrm{K})$')
    ax1.set_ylabel(r'$\log_{10}(L/L_{\odot})$')
    ax1.set_title('赫罗图 (HR Diagram)')
    ax1.grid(True, alpha=0.3)
    plt.colorbar(scatter1, ax=ax1, label='年龄 (年)')
    
    # 图2：光度随时间变化
    ax2 = axes[0, 1]
    ax2.plot(age, log_L, 'b-', linewidth=1.5)
    ax2.set_xlabel('年龄 (年)')
    ax2.set_ylabel(r'$\log_{10}(L/L_{\odot})$')
    ax2.set_title('光度演化')
    ax2.grid(True, alpha=0.3)
    ax2.set_xscale('log')
    
    # 图3：温度随时间变化
    ax3 = axes[1, 0]
    ax3.plot(age, log_teff, 'r-', linewidth=1.5)
    ax3.set_xlabel('年龄 (年)')
    ax3.set_ylabel(r'$\log_{10}(T_{\mathrm{eff}}/\mathrm{K})$')
    ax3.set_title('表面温度演化')
    ax3.grid(True, alpha=0.3)
    ax3.set_xscale('log')
    
    # 图4：半径随时间变化（如果存在）
    if 'log_R' in data_dict:
        ax4 = axes[1, 1]
        ax4.plot(age, data_dict['log_R'], 'g-', linewidth=1.5)
        ax4.set_xlabel('年龄 (年)')
        ax4.set_ylabel(r'$\log_{10}(R/R_{\odot})$')
        ax4.set_title('半径演化')
        ax4.grid(True, alpha=0.3)
        ax4.set_xscale('log')
    
    plt.tight_layout()
    plt.savefig('stellar_evolution_summary.png', dpi=300, bbox_inches='tight')
    print("图片已保存为 'stellar_evolution_summary.png'")
    plt.show()

def main():
    """
    主函数
    """
    file_path = 'LOGS/history.data'
    
    print("="*60)
    print("MESA演化数据分析")
    print("="*60)
    
    # 读取数据
    data_dict, columns = read_mesa_fixed_width(file_path)
    
    if data_dict is None:
        print("无法读取数据，程序终止")
        return
    
    # 打印前几个数据点
    print(f"\n前5个模型的数据:")
    for col in ['model_number', 'star_age', 'log_Teff', 'log_L']:
        if col in data_dict:
            values = data_dict[col][:5]
            print(f"  {col}: {values}")
    
    # 绘制赫罗图
    print("\n" + "="*60)
    print("绘制赫罗图")
    print("="*60)
    
    if plot_simple_hr_diagram(data_dict):
        print("✓ 成功绘制赫罗图")
    
    # 绘制更多图表（可选）
    response = input("\n是否绘制更多图表？(y/n): ")
    if response.lower() == 'y':
        print("\n绘制多图分析...")
        plot_multiple_plots(data_dict)
    
    print("\n" + "="*60)
    print("分析完成！")
    print("="*60)

if __name__ == "__main__":
    main()
