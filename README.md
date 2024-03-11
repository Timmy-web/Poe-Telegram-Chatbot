# Poe-Telegram-Chatbot

这是一个使用 Python 和 Telegram Bot API 构建的聊天机器人,它利用了 Poe API 提供的 AI 模型进行纯文字对话。（暂不支持上传图片，文件）

## 功能特点

- 支持与 GPT-4 和 Claude-3-Opus 模型进行对话
- 可以保持对话上下文,实现连续对话
- 提供命令切换不同的 AI 模型
- 支持 Docker 容器化部署

## 安装与运行

### 前置要求

- Python 3.9 (经过测试)
- [Poe API 密钥](https://poe.com/api_key)
- Telegram Bot Token (通过 BotFather 获取)

### 本地运行

1. 克隆此仓库:
```bash
git clone https://github.com/Timmy-web/Poe-Telegram-Chatbot.git
cd Poe-Telegram-Chatbot
```

2. 安装依赖:
```bash
pip install -r requirements.txt
```

3. 设置环境变量:
```bash
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token"
export POE_API_KEY="your_poe_api_key"
```

4. 运行 bot:
```bash
python bot.py
```

### Docker 运行

运行 Docker 容器:
```bash
docker run -d --name poebot \
  -e TELEGRAM_BOT_TOKEN="your_telegram_bot_token" \
  -e POE_API_KEY="your_poe_api_key" \
  ghcr.io/timmy-web/poe-bot
```
或者使用 docker-compose:
```bash
docker-compose up -d
```
注意将 your_telegram_bot_token 和 your_poe_api_key 替换为你自己的 Token 和 API 密钥。

## 使用方法

- `/start` - 开始与机器人对话 
- `/new` - 开始一个新的对话,清空上下文
- `/gpt4` - 切换到 GPT-4 模型
- `/claude3` - 切换到 Claude-3-Opus 模型

直接在聊天界面输入问题,机器人就会自动回复。
