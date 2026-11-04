# ERP 采购智能助手

## 项目概述

本项目是一个面向 ERP 采购业务的 AI 对话应用，采用 Vue 3 前端、FastAPI 后端，以及基于 DeepAgents、LangChain 和 LangGraph 的智能体架构。

用户通过聊天界面提出采购需求，主智能体协调采购分析和订单处理两个子智能体，通过 MCP 工具访问外部 Java 业务后端，并结合网页搜索、图表生成和沙箱执行能力完成任务。

## 核心功能

- **采购业务交互**：提供供应商、零件、库存和采购订单相关业务工具。
- **多智能体协作**：主智能体协调任务，采购分析与订单处理子智能体分别执行对应工作。
- **流式对话**：通过 SSE 持续返回回答、工具调用和子智能体执行信息。
- **人工交互与恢复**：支持执行过程中请求用户补充信息，并在收到回复后恢复任务。
- **历史会话管理**：支持会话列表、消息查询、会话删除和标题修改。
- **搜索与可视化**：集成网页搜索及统一图表生成工具。
- **技能扩展**：通过技能文件和 YAML 子智能体配置扩展能力。
- **沙箱执行**：按用户管理沙箱，提供健康检查、恢复、错误处理和熔断机制。

## 技术架构

```text
用户
  ↓
Vue 3 聊天前端
  ↓ HTTP / SSE
FastAPI API 服务
  ↓
主智能体
  ├─ 采购分析子智能体
  ├─ 采购订单子智能体
  ├─ 网页搜索与图表工具
  ├─ 技能管理与沙箱文件下载
  └─ 用户沙箱执行环境

业务工具 → MCP 服务 → 外部 Java ERP REST API

对话状态与展示消息 → MongoDB
记忆和技能 Store → 当前使用 InMemoryStore
```

应用启动时预加载 MCP 工具、图表工具和子智能体配置。处理请求时，再结合用户对应的沙箱构建智能体执行图，以复用公共组件并隔离用户执行环境。

## 技术栈

| 层级 | 主要技术 |
|---|---|
| 前端 | Vue 3、Vite、Axios |
| 消息展示 | markdown-it、highlight.js |
| API 服务 | FastAPI、Uvicorn、SSE |
| 智能体编排 | DeepAgents、LangChain、LangGraph |
| 业务工具协议 | FastMCP、langchain-mcp-adapters |
| 对话持久化 | MongoDB、MongoDBSaver |
| 执行环境 | OpenSandbox 相关后端封装 |
| 配置与技能 | YAML、Markdown、Python |
| Python 版本 | 项目声明要求 Python 3.12 及以上 |

## 目录结构

```text
PythonProject3/
├─ frontend/                 # Vue 聊天前端
│  └─ src/
│     ├─ api/                # 对话与历史记录接口
│     ├─ components/         # 消息、侧栏、输入、工具调用等组件
│     └─ styles/             # 页面样式
├─ src/
│  ├─ agent/                 # 智能体核心
│  │  ├─ backends/           # 沙箱管理与后端适配
│  │  ├─ memory/             # 记忆相关定义与提示词
│  │  ├─ middlewares/        # 上下文、摘要、技能同步与异常处理
│  │  ├─ subagents/          # 子智能体加载器及 YAML 配置
│  │  ├─ tools/              # 搜索、图表、人工交互等工具
│  │  └─ main_agent.py       # 主智能体构建入口
│  ├─ api_view/              # FastAPI 应用与接口
│  ├─ mcp_server/            # Java 业务接口的 MCP 封装
│  ├─ skills/                # 采购及技能管理能力
│  └─ test/                  # 智能体和 MCP 测试脚本
├─ test/                     # 其他实验、示例与测试代码
├─ start_web.py              # 前后端联合启动脚本
├─ pyproject.toml            # Python 项目元数据
└─ requirements.txt          # Python 依赖清单
```

## 主要模块

### 智能体编排

`src/agent/main_agent.py` 负责组合模型、工具、子智能体、中间件、记忆及检查点存储。

两个子智能体通过 YAML 定义：

- `procurement-analyst`：采购分析。
- `procurement-order`：采购订单处理。

工具名称在加载时与实际工具匹配，随后注入对应子智能体。

### 业务工具服务

`src/mcp_server/` 使用 FastMCP，将外部 Java 后端 REST API 包装为智能体可调用的工具，分为供应商、零件、库存和订单四组，并采用 Streamable HTTP 提供服务。

### 对话与历史记录

`src/api_view/` 提供流式聊天、任务恢复、状态查询及历史记录管理接口。

| 方法 | 路径 | 用途 |
|---|---|---|
| POST | `/api/chat/stream` | 发起流式对话 |
| POST | `/api/chat/{thread_id}/resume` | 恢复中断任务 |
| GET | `/api/chat/{thread_id}` | 查询会话状态 |
| GET | `/api/history` | 获取会话列表 |
| GET | `/api/history/{thread_id}/messages` | 获取会话消息 |
| DELETE | `/api/history/{thread_id}` | 删除会话 |
| PATCH | `/api/history/{thread_id}` | 修改会话标题 |
| GET | `/health` | 服务健康检查 |

### 状态与记忆

项目使用 MongoDB 保存智能体对话检查点，并保存用于前端展示的完整消息，包括子智能体消息。

记忆和技能所使用的 Store 当前为 `InMemoryStore`，这部分数据尚不能视为具备跨进程重启的持久化能力。

### 执行稳定性

中间件提供沙箱健康检查、工具异常捕获、上下文注入、技能同步与恢复、对话摘要和记忆更新，并设置模型及工具调用次数上限。

## 启动方式

在依赖及外部服务已准备好的情况下，项目提供联合启动入口：

```bash
python start_web.py
```

该脚本启动后端，等待健康检查通过后再启动前端；如果前端依赖目录不存在，会尝试安装依赖。

脚本中配置的访问地址：

- 前端：`http://localhost:3000`
- 后端：`http://localhost:8090`
- API 文档：`http://localhost:8090/docs`

联合启动脚本只负责前后端进程。完整业务运行还依赖模型服务、MongoDB、沙箱服务、相关 MCP 服务及外部 Java ERP 后端。

## 当前实现说明

本项目已包含聊天界面、智能体编排、业务工具接入、沙箱管理和会话存储代码。

`pyproject.toml` 中声明的依赖较少，未覆盖代码中使用的全部主要框架，因此不能仅凭该文件判断运行环境已完整配置。

本文基于源代码静态阅读整理，未执行启动、测试或外部服务连接验证；所列功能描述的是代码中的实现，不代表已通过运行验收。
