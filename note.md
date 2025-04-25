使用 hd-bet 時，要去 anaconda3\envs\{your_env}\lib\site-packages\HD_BET\utils.py 的 maybe_download_parameters 函數中(27 行)

maybe_mkdir_p(folder_with_parameter_files) 改為 os.makedirs(folder_with_parameter_files, exist_ok=True)


根據需求安裝 gpu 版 torch
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
