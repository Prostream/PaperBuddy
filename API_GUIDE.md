# PaperBuddy API Guide

这是PaperBuddy项目的API开发指南，使用**RESTful API架构**，每个模块独立开发。

## 📋 目录

- [总体架构](#总体架构)
- [API路由总览](#api路由总览)
- [模块A：输入解析](#模块a输入解析-person-1)
- [模块B：LLM总结](#模块bllm总结-person-2)
- [模块C：图像生成](#模块c图像生成-person-3)
- [模块D：前端整合](#模块d前端整合--pdf导出-person-4)
- [测试指南](#测试指南)

---

## 总体架构

### 数据流

```
输入 (PDF/Manual)
    ↓
【Module A】 /api/parse/pdf 或 /api/parse/manual
    ↓ (返回 paperData)
【Module B】 /api/summarize
    ↓ (返回 summary)
【Module C】 /api/images/generate
    ↓ (返回 images)
【Module D】 前端渲染 + PDF导出
```

### 技术栈

- **后端**: Flask 3.0 (Python)
- **前端**: React 19.1 + Vite 7.1
- **状态管理**: React useState (无需Redux/Vuex)
- **数据传输**: JSON格式

---

## API路由总览

| 路由 | 方法 | 负责人 | 功能 |
|------|------|--------|------|
| `/api/parse/pdf` | POST | Person 1 | 解析PDF文件 |
| `/api/parse/manual` | POST | Person 1 | 验证手动输入 |
| `/api/summarize` | POST | Person 2 | LLM生成摘要 |
| `/api/images/generate` | POST | Person 3 | 生成插图 |

---

## 模块A：输入解析 (Person 1)

### 职责
- 解析PDF文件提取结构化数据
- 验证和标准化手动输入数据

### 路由1: `/api/parse/pdf`

**请求格式**:
```http
POST /api/parse/pdf
Content-Type: multipart/form-data

file: <PDF文件>
courseTopic: CV | NLP | Systems
```

**响应格式**:
```json
{
  "title": "论文标题",
  "authors": ["作者1", "作者2"],
  "abstract": "摘要内容...",
  "sections": [
    {
      "heading": "Introduction",
      "content": "章节内容..."
    }
  ],
  "courseTopic": "CV"
}
```

**TODO清单**:
1. ✅ 安装依赖: `pip install PyPDF2`
2. ⬜ 读取PDF文件内容
3. ⬜ 提取metadata（标题、作者）
4. ⬜ 识别abstract部分
5. ⬜ 按章节切分内容
6. ⬜ 错误处理（文件损坏、格式不支持等）

**实现位置**: `server/app.py` 第51-113行

---

### 路由2: `/api/parse/manual`

**请求格式**:
```http
POST /api/parse/manual
Content-Type: application/json

{
  "title": "论文标题",
  "authors": "作者1, 作者2, 作者3",
  "abstract": "摘要内容",
  "sections": [
    {"heading": "Introduction", "content": "..."}
  ],
  "courseTopic": "NLP"
}
```

**响应格式**: 同上（标准化后）

**TODO清单**:
1. ✅ 基本字段验证（title, authors, abstract必填）
2. ⬜ 深度验证（长度限制、格式检查）
3. ⬜ Authors字符串解析为数组
4. ⬜ 清理和标准化sections
5. ⬜ 返回统一格式

**实现位置**: `server/app.py` 第116-190行

---

## 模块B：LLM总结 (Person 2)

### 职责
- 使用LLM生成Like-I'm-Five风格摘要
- 提取关键概念和教学辅助信息

### 路由: `/api/summarize`

**请求格式**:
```http
POST /api/summarize
Content-Type: application/json

{
  "title": "论文标题",
  "authors": ["作者1"],
  "abstract": "摘要...",
  "sections": [...],
  "courseTopic": "Systems"
}
```

**响应格式**:
```json
{
  "big_idea": "一句话核心思想（≤12词）",
  "steps": [
    "步骤1：简单描述",
    "步骤2：...",
    "步骤3：..."
  ],
  "example": "真实世界的例子说明",
  "why_it_matters": "为什么重要",
  "limitations": "局限性",
  "glossary": [
    {"term": "术语1", "definition": "简单解释"}
  ],
  "for_class": {
    "prerequisites": ["前置知识1", "前置知识2"],
    "connections": ["与XX主题相关"],
    "discussion_questions": ["问题1?", "问题2?"]
  },
  "accuracy_flags": ["不确定的地方"]
}
```

**TODO清单**:
1. ✅ 安装依赖: `pip install openai` (或 `anthropic`)
2. ⬜ 设置API key: `.env` 中添加 `OPENAI_API_KEY=sk-xxx`
3. ⬜ 设计prompt模板:
   - Like-I'm-Five语气
   - 短句子（≤12词）
   - 强制JSON输出
   - 包含courseTopic上下文
4. ⬜ 调用LLM API
5. ⬜ 解析和验证JSON响应
6. ⬜ 错误处理和重试逻辑
7. ⬜ 超时处理（建议60秒）

**Prompt示例**:
```python
prompt = f"""
You are an expert teacher explaining research papers to 5-year-olds.

Course Topic: {course_topic}
Paper Title: {title}
Abstract: {abstract}

Create a kid-friendly summary in JSON format:
{{
  "big_idea": "one sentence (≤12 words)",
  "steps": ["step1", "step2", "step3"],
  "example": "real-world analogy",
  ...
}}

Use simple words. Keep sentences short.
"""
```

**实现位置**: `server/app.py` 第197-320行

---

## 模块C：图像生成 (Person 3)

### 职责
- 根据关键概念生成kid-friendly插图
- 处理图像生成失败的fallback

### 路由: `/api/images/generate`

**请求格式**:
```http
POST /api/images/generate
Content-Type: application/json

{
  "key_points": [
    "关键概念1",
    "关键概念2",
    "关键概念3"
  ],
  "style": "pastel"
}
```

**响应格式**:
```json
{
  "images": [
    {
      "url": "https://...或base64字符串",
      "description": "图像描述",
      "key_point": "对应的关键概念"
    }
  ]
}
```

**TODO清单**:
1. ✅ 选择图像生成API:
   - DALL-E 3: `pip install openai`
   - Stable Diffusion: `pip install replicate`
2. ⬜ 设置API key
3. ⬜ 为每个key_point生成prompt:
   - 添加style关键词（pastel, cute, colorful）
   - 保持kid-friendly风格
4. ⬜ 调用图像生成API
5. ⬜ 处理rate limiting（限制3-5张）
6. ⬜ 实现fallback:
   - 失败时返回placeholder URL
   - 或返回简单彩色矩形
7. ⬜ 返回图像数组

**Prompt示例**:
```python
prompt = f"kid-friendly pastel illustration: {key_point}, simple, cute, colorful, children's book style"
```

**实现位置**: `server/app.py` 第327-421行

---

## 模块D：前端整合 & PDF导出 (Person 4)

### 职责
- 整合所有API调用
- 设计最终展示页面
- 实现PDF导出功能
- 全局Layout和样式

### 前端API调用

所有API调用已封装在 `client/src/api.js`：

```javascript
import { executeFullPipeline } from './api'

// 执行完整流程
const result = await executeFullPipeline({
  type: 'pdf',        // 或 'manual'
  data: pdfFile,      // 或 manualData对象
  courseTopic: 'CV'
})

// result包含:
// - paperData: 解析后的论文数据
// - summary: LLM生成的摘要
// - images: 生成的图片数组
```

### 展示页面结构

建议的最终页面布局：

```
┌─────────────────────────────────────┐
│  Header (论文标题 + 作者)             │
├─────────────────────────────────────┤
│  Big Idea (突出显示)                  │
├─────────────────────────────────────┤
│  How It Works (Steps)                │
│  ┌──────┐  ┌──────┐  ┌──────┐       │
│  │ IMG1 │  │ IMG2 │  │ IMG3 │       │
│  └──────┘  └──────┘  └──────┘       │
├─────────────────────────────────────┤
│  Example & Why It Matters            │
├─────────────────────────────────────┤
│  Glossary (术语表)                    │
├─────────────────────────────────────┤
│  For Class Section                   │
│  - Prerequisites                     │
│  - Connections                       │
│  - Discussion Questions              │
├─────────────────────────────────────┤
│  Limitations & Accuracy Flags        │
├─────────────────────────────────────┤
│  [ Export as PDF ] Button            │
└─────────────────────────────────────┘
```

### PDF导出实现

1. ✅ 安装依赖: `npm install html2pdf.js`
2. ⬜ 创建导出函数:

```javascript
import html2pdf from 'html2pdf.js'

const exportToPDF = () => {
  const element = document.getElementById('final-result')

  const options = {
    margin: 0.5,
    filename: 'paper-summary.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  }

  html2pdf().set(options).from(element).save()
}
```

3. ⬜ 优化打印样式:

```css
@media print {
  /* 隐藏导航和按钮 */
  .no-print { display: none; }

  /* 调整字体和间距 */
  body { font-size: 12pt; }
}
```

### TODO清单
1. ⬜ 实现完整的渲染组件（ResultDisplay.jsx）
2. ⬜ 添加Light/Dark模式切换
3. ⬜ 实现PDF导出功能
4. ⬜ 优化移动端响应式
5. ⬜ 添加打印样式
6. ⬜ 实现全局Loading状态
7. ⬜ 错误处理UI

**实现位置**:
- `client/src/App.jsx` (主应用)
- `client/src/api.js` (API调用)
- `client/src/ResultDisplay.jsx` (待创建)

---

## 测试指南

### 1. 独立测试每个模块

**模块A测试**:
```bash
curl -X POST http://localhost:5175/api/parse/pdf \
  -F "file=@test.pdf" \
  -F "courseTopic=CV"
```

**模块B测试**:
```bash
curl -X POST http://localhost:5175/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Paper",
    "authors": ["Alice"],
    "abstract": "This is a test abstract",
    "sections": [],
    "courseTopic": "NLP"
  }'
```

**模块C测试**:
```bash
curl -X POST http://localhost:5175/api/images/generate \
  -H "Content-Type: application/json" \
  -d '{
    "key_points": ["Neural networks", "Training data"],
    "style": "pastel"
  }'
```

### 2. 前端集成测试

```bash
# 启动后端
cd server
python app.py

# 启动前端
cd client
npm run dev

# 访问 http://localhost:5173
```

### 3. Mock数据测试

在实现真实API之前，可以先用mock数据测试：

```javascript
// 在api.js中临时添加
export async function parsePDF(pdfFile, courseTopic) {
  // 返回mock数据用于测试
  return {
    title: "Mock Paper Title",
    authors: ["Mock Author"],
    abstract: "Mock abstract...",
    sections: []
  }
}
```

---

## 环境变量配置

### 后端 `.env` 文件

```bash
# server/.env
PORT=5175
APP_VERSION=0.1.0
CORS_ORIGIN=http://localhost:5173

# Person 2: LLM API Key
OPENAI_API_KEY=sk-xxxxxxxx
# 或
ANTHROPIC_API_KEY=sk-ant-xxxxxxxx

# Person 3: Image Generation API Key
REPLICATE_API_TOKEN=r8_xxxxxxxx
```

### 前端 `.env` 文件

```bash
# client/.env
VITE_API_URL=http://localhost:5175
```

---

## 常见问题

### Q1: 如何调试API？

使用Flask的debug模式（已启用）：
```python
app.run(debug=True)
```

查看后端日志：
```bash
cd server
python app.py
# 所有请求会打印在终端
```

### Q2: CORS错误怎么办？

确认：
1. Flask-CORS已配置（已完成）
2. 前端API URL正确
3. 后端服务已启动

### Q3: 如何快速测试单个endpoint？

使用`curl`或Postman，或者在浏览器DevTools中：

```javascript
fetch('http://localhost:5175/api/health')
  .then(r => r.json())
  .then(console.log)
```

### Q4: 图片太大导致响应慢怎么办？

建议：
1. 限制图片数量（3-5张）
2. 使用较小的尺寸（512x512）
3. 返回URL而不是base64
4. 实现图片缓存

---

## 集成时间表建议

### Week 1: 独立开发
- 每个人实现自己的API endpoint
- 使用mock数据测试
- 完成基本功能

### Week 2: 接口对接
- 统一JSON schema
- 测试API调用链路
- 修复bug

### Week 3: 整合和优化
- Person 4整合所有模块
- 优化UI/UX
- 实现PDF导出

### Week 4: 测试和Demo
- 端到端测试
- 准备演示材料
- 修复最后问题

---

## 联系方式

遇到问题时的沟通流程：
1. 检查本文档和代码注释
2. 查看`server/app.py`中的TODO
3. 在团队群里讨论
4. 更新此文档

---

**祝开发顺利！🎉**
