#基于python的基础镜像
FROM python:3.11.7

#设置code文件夹是工作目录
WORKDIR /code

COPY . .

#安装支持 -i 换国内pip源
RUN pip install -r /code/requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/


CMD ["python", "/code/main.py"]
