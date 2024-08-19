# deriw bot

### 安装环境

1. 安装python环境
2. 安装依赖：`pip3 install web3`

### 批量生成账号

1. [安装环境](#安装环境)
2. 进入`script`目录，执行`python3 gene_account.py`

会在当前目录生成`batch_acc.txt`文件

### 领水

1. [安装环境](#安装环境)
2. 将私钥放入`pk.txt`。或者将生成`batch_acc.txt`文件内容copy到`pk.txt`中。
3. 进入`script`目录，执行`python3 claim.py`  


### 市价做多

1. [安装环境](#安装环境)
2. 将私钥放入`pk.txt`。或者将生成`batch_acc.txt`文件内容copy到`pk.txt`中。
3. 进入`script`目录，执行`python3 mark_long.py`  