#!/bin/bash
# Streamlit Cloud 部署前设置脚本
# 确保安装 CPU 版本的 PyTorch（云平台无 GPU）

pip install torch --index-url https://download.pytorch.org/whl/cpu
