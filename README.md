# faq_chatbot
基于deeppavlov +tfidf + logreg 实现chatbot faq 聊天功能

## clone 项目到本地

#### 1.创建虚拟环境，安装项目依赖
> pip install -r requirements.txt



## 添加自己的faq.json文件,文件路径：faq_chatbot/train_data/lancome/0.1/faq.json

## 训练模型 python ./train.py --version 0.1 --bot_id lancome --croups_dir ./train_data/ --output_dir ./chat_model/


## 运行app.py 启动文件 启动项目
