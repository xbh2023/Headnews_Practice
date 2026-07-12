/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

export const aiChatConfig = {
  // OpenAI API地址
  apiEndpoint: 'https://api.deepseek.com/chat/completions',
  
  // API Key (由开发人员指定)
  apiKey: 'sk-d1a11510fc5e47b4b8ce9ca2534bc1e5',
  
  // 使用的模型
  model: 'deepseek-v4-pro'
}
