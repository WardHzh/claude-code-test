# Claude Code 智能体与 Skill 开发部署完全指南

> 整理时间：2026-05-15  
> 基于 Anthropic 官方文档、社区实践与最新生态资源

---

## 目录

1. [概述：什么是 Claude Code Agent 开发](#1-概述什么是-claude-code-agent-开发)
2. [Harness Engineering：Agent 开发的核心范式](#2-harness-engineeringagent-开发的核心范式)
3. [Skill 开发详解](#3-skill-开发详解)
   - [3.1 什么是 Skill](#31-什么是-skill)
   - [3.2 SKILL.md 结构](#32-skillmd-结构)
   - [3.3 元数据字段详解](#33-元数据字段详解)
   - [3.4 渐进式披露（Progressive Disclosure）](#34-渐进式披露progressive-disclosure)
   - [3.5 目录位置与加载规则](#35-目录位置与加载规则)
   - [3.6 编写最佳实践](#36-编写最佳实践)
4. [Skill 高级模式](#4-skill-高级模式)
   - [4.1 主/副 Skill 模式（自改进 Agent）](#41-主副-skill-模式自改进-agent)
   - [4.2 Skill 链（Skill Chaining）](#42-skill-链skill-chaining)
   - [4.3 Subagent 上下文隔离](#43-subagent-上下文隔离)
   - [4.4 与 MCP 服务器组合](#44-与-mcp-服务器组合)
5. [Claude Agent SDK 开发](#5-claude-agent-sdk-开发)
   - [5.1 SDK 安装](#51-sdk-安装)
   - [5.2 核心 API](#52-核心-api)
   - [5.3 自定义工具开发](#53-自定义工具开发)
   - [5.4 与 Messages API 集成](#54-与-messages-api-集成)
6. [部署方案](#6-部署方案)
   - [6.1 Claude Code 本地部署](#61-claude-code-本地部署)
   - [6.2 Managed Agents API 部署](#62-managed-agents-api-部署)
   - [6.3 国内部署与替代方案](#63-国内部署与替代方案)
   - [6.4 企业级部署清单](#64-企业级部署清单)
7. [CLAUDE.md 配置最佳实践](#7-claudemd-配置最佳实践)
8. [常见错误与解决方案](#8-常见错误与解决方案)
9. [资源汇总](#9-资源汇总)

---

## 1. 概述：什么是 Claude Code Agent 开发

**Claude Code** 是 Anthropic 推出的终端 AI 编程 Agent，可直接在终端中读/写文件、执行命令、编排多步工作流。到 2026 年，已发展出成熟的 **Harness Engineering（工程化编排）** 方法论。

核心公式：

```
Coding Agent = AI 模型 + Harness（工程化编排层）
```

**Harness 包含：**

| 组件 | 作用 | 示例 |
|------|------|------|
| **Rules 文件** (`CLAUDE.md`) | 每次会话自动加载的持久指令 | 构建命令、代码风格、注意事项 |
| **Skills** (`SKILL.md`) | 按需激活的复用指令集 | 领域专业知识、工作流模板 |
| **MCP 服务器** | 外部工具/API 连接 | GitHub、数据库、搜索引擎 |
| **Hooks** | 生命周期事件的确定性脚本 | 自动格式化、任务前后处理 |
| **Sub-agents** | 隔离的 Claude 子实例 | 代码库研究、安全审查 |

---

## 2. Harness Engineering：Agent 开发的核心范式

2026 年的 Agent 开发不再只是"写好 prompt"，而是系统地配置 Agent 周围的整套环境：

### 开发循环

```
计划 (Plan Mode) → 实现 → 审查 → 测试 → 部署 → 监控 → 迭代
```

### Agent 开发的三层渐进架构

```
┌─────────────────────────────────────┐
│  Layer 1: 元数据                      │
│  名称 + 描述（始终在上下文中）          │
├─────────────────────────────────────┤
│  Layer 2: Skill 正文                 │
│  SKILL.md 完整指令（触发时加载）       │
├─────────────────────────────────────┤
│  Layer 3: 附属资源                    │
│  脚本 / 参考资料 / 模板（按需加载）     │
└─────────────────────────────────────┘
```

### 关键原则

- **渐进式披露**：不将所有信息一次性塞入上下文，只在需要时加载
- **最小权限**：Skill 应限制 `allowed-tools`，避免越权操作
- **输出契约**：定义明确的 JSON 输出格式，便于链式调用

---

## 3. Skill 开发详解

### 3.1 什么是 Skill

Skill 是 Claude Code 的可复用能力单元。每个 Skill 是一个文件夹，核心是 `SKILL.md` 文件。Claude 会根据用户请求自动判断并加载相关的 Skill。

> **Skill vs MCP**：Skill 是上下文中的指令，MCP 是外部工具连接。Skill 更轻量、标准化程度更高、可控性更强。

### 3.2 SKILL.md 结构

```
.claude/skills/<skill-name>/
├── SKILL.md              # 必需：YAML 前置元数据 + 指令正文
├── scripts/              # 可选：确定性辅助脚本（优先用标准库）
├── references/           # 可选：领域知识库（按需加载）
├── assets/               # 可选：模板、示例数据、期望输出
├── agents/               # 可选：子 Agent 定义
├── commands/             # 可选：斜杠命令定义
└── evals/
    └── evals.json        # 可选：测试用例 + 断言
```

### 3.3 元数据字段详解

```yaml
---
name: <skill-name>              # 必需：小写字母+连字符，≤64 字符
description: <summary>          # 必需：自动触发摘要，≤1024 字符
allowed-tools:                  # 可选：限制可用工具
  - Read
  - Edit
  - Write
context: fork                   # 可选：在隔离子 Agent 上下文中运行
agent:                          # 可选：子 Agent 定义
  name: <agent-name>
  model: claude-sonnet-4-20250514
hooks:                          # 可选：生命周期钩子
  pre-load: !command <shell>
model:                          # 可选：指定使用的模型
disable-model-invocation: true  # 可选：禁止自动调用
---
```

**description 编写要点：**
- 使用第三人称（"This skill should be used when..."）
- 前 150-200 字符是关键匹配区
- 包含触发词和边界条件

### 3.4 渐进式披露（Progressive Disclosure）

| 层级 | 内容 | 可见性 | 大小限制 |
|------|------|--------|----------|
| Layer 1 | 元数据（name + description） | 始终在上下文中 | ~100 词 |
| Layer 2 | SKILL.md 正文 | 触发时加载 | 1,500-2,000 词最优 |
| Layer 3 | references/scripts/assets | 按需加载 | 无硬限制 |

### 3.5 目录位置与加载规则

| 位置 | 作用域 | 说明 |
|------|--------|------|
| `~/.claude/skills/` | 全局（用户级） | 所有项目均可访问 |
| `<project>/.claude/skills/` | 项目级 | 仅当前项目可用 |
| `<project>/packages/*/.claude/skills/` | 嵌套（Monorepo） | 自动加载子目录规则 |

### 3.6 编写最佳实践

**DO：**
- 使用祈使句 / 不定式（verb-first）："Inspect the CSV"，"Compute statistics"
- 保持 SKILL.md 精简（≤ 500 行为宜）
- 定义明确的输入输出契约
- 使用 `**` 标记关键规则
- 包含 Why / How to apply 解释

**DON'T：**
- 使用第二人称（"you should"）
- 在 SKILL.md 中塞入大量参考资料（应放在 references/ 目录）
- 描述过于宽泛导致误触发

**最小 SKILL.md 模板：**

```markdown
---
name: csv-insights
description: Inspect a small CSV and return JSON insights with summary stats, outliers, and business takeaways.
---

## Purpose
Provide quick, trustworthy insights from a CSV file.

## Instructions
1. Identify column types and check row counts.
2. Compute descriptive stats per numeric column.
3. Flag anomalies and missing-data patterns.
4. Produce 3 business-relevant takeaways.

## Output
```json
{
  "columns": [{"name": "string", "type": "string"}],
  "stats": {"<column>": {"min": 0, "max": 0, "mean": 0, "missing": 0}},
  "outliers": [{"row": 0, "reason": "string"}],
  "takeaways": ["string", "string", "string"]
}
```
```

---

## 4. Skill 高级模式

### 4.1 主/副 Skill 模式（自改进 Agent）

```
project_root/
└── .claude/skills/
    ├── primary/SKILL.md      # 通过 hooks 自动注入每次会话
    ├── database/SKILL.md     # 检测到数据库工作时加载
    ├── api-design/SKILL.md   # API 开发时加载
    └── ui-dev/SKILL.md       # UI 修改时加载
```

**错误学习机制** — 每次错误都更新 Skill 规则：

```markdown
### [规则名称]
**规则:** [始终/绝不做什么]
**错误示例:** `[失败的模式]`
**正确示例:** `[有效的方式]`
**原因:** [根因分析]
```

### 4.2 Skill 链（Skill Chaining）

将多个 Skill 串联，每个步骤有明确的输入/输出契约：

```
csv-insights → monthly-report → pptx-export → send-email
```

- 每个 Skill 以 JSON 格式输出
- 使用 Subagent 隔离各步骤
- 最后汇总并审查差异

### 4.3 Subagent 上下文隔离

Subagent 在独立的上下文窗口中运行：

- **防止主上下文污染** — 长期会话中节省 40%+ 的输入 token
- 适用于：代码库研究、安全审查、大规模重构
- 用法：在 SKILL.md 中设置 `context: fork`

### 4.4 与 MCP 服务器组合

Skill + MCP 实现强大功能：

| 组合 | 用例 |
|------|------|
| Skill + GitHub MCP | 自动提 PR、Code Review |
| Skill + Database MCP | NL2SQL 查询分析 |
| Skill + Feishu MCP | 发送消息、创建文档 |
| Skill + Milvus MCP | 搭建 RAG 知识库 |

---

## 5. Claude Agent SDK 开发

### 5.1 SDK 安装

```bash
# Python SDK
pip install claude-agent-sdk

# TypeScript SDK
npm install @anthropic-ai/claude-agent-sdk

# 或者作为 AI SDK 提供者
npm install ai-sdk-claude-agent-provider ai
```

### 5.2 核心 API

```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Agent SDK 关键组件：**
- **Agent Loop** — 主循环，管理对话状态
- **Tools** — 工具定义与执行
- **Subagents** — 子 Agent 管理
- **Hooks** — 生命周期钩子
- **MCP** — 与 MCP 服务器集成

### 5.3 自定义工具开发

```python
# Python — 使用 @tool 装饰器
from claude_agent_sdk import tool

@tool
def search_docs(query: str) -> str:
    """Search internal documentation."""
    return search_engine(query)
```

```typescript
// TypeScript
import { tool } from "@anthropic-ai/claude-agent-sdk";

const searchDocs = tool({
  name: "search_docs",
  description: "Search internal documentation",
  parameters: { query: { type: "string" } },
  execute: async ({ query }) => searchEngine(query),
});
```

### 5.4 与 Messages API 集成

```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=2048,
    betas=["skills-2025-10-02"],
    container={
        "skills": [
            {"type": "anthropic", "skill_id": "pptx", "version": "latest"},
            {"type": "anthropic", "skill_id": "docx", "version": "latest"},
        ]
    },
    messages=[{"role": "user", "content": "Create a 6-slide deck..."}]
)
```

> 限制：Messages API 每次最多 8 个 Skill，Managed Agents API 每会话最多 20 个。

---

## 6. 部署方案

### 6.1 Claude Code 本地部署

```bash
# 安装 Claude Code CLI
npm install -g @anthropic-ai/claude-code

# 启动交互式会话
claude

# 一次性任务
claude "分析这个项目结构"
```

### 6.2 Managed Agents API 部署

用于云端生产环境：

```python
# 创建托管 Agent
response = client.managed_agents.create(
    name="my-agent",
    model="claude-sonnet-4-20250514",
    skills=[
        {"type": "anthropic", "skill_id": "code-review"},
        {"type": "custom", "path": "./skills/my-skill"}
    ],
    permissions={
        "tools": ["Read", "Edit", "Write", "Bash"]
    }
)
```

**部署流程：**
1. **开发** — 本地编写 Skill 并测试
2. **版本锁定** — 锁定 Skill 版本号（避免使用 `"latest"`）
3. **权限配置** — 在 SDK 层面统一管理工具权限
4. **CI/CD 集成** — 使用 CI 检查 Skill 格式、运行评估
5. **监控** — 记录 Skill 选择、工具调用、生成产物
6. **灰度发布** — Dev → Staging → Prod 逐步推广

### 6.3 国内部署与替代方案

| 方案 | 说明 | 安装 |
|------|------|------|
| **OpenClaude CN** | 用国产大模型驱动 Claude Code（通义千问、DeepSeek、GLM 等） | `npm i -g @khalilgao/openclaude-cn` |
| **claude-code-zh** | 中文 Skills + Rules + Prompts 包 | `curl -fsSL https://raw.githubusercontent.com/huanglei288766/claude-code-zh/main/install.sh \| bash` |
| **claude-init-CN** | 中文开发套件，含 MCP 服务器、安全扫描 | `curl -fsSL https://raw.githubusercontent.com/cfrs2005/claude-init/main/install.sh \| bash` |
| **阿里云 ECS 一键部署** | 在 Agentic OS ECS 上一句话部署 | 阿里云控制台操作 |

### 6.4 企业级部署清单

| 检查项 | 说明 |
|--------|------|
| 最小权限原则 | 限制 `allowed-tools` 和文件系统权限 |
| 审批门控 | 高风险操作要求 Plan Mode 审批 |
| 版本控制 | Skill 纳入 Git 管理，CI 检查格式 |
| 监控与可观测性 | 追踪采纳率、错误率、每次运行成本 |
| 规则过期管理 | 为规则添加 Retire when 条件 |
| 成本控制 | 设置预算，监控 Token 消耗和延迟 |
| 输出验证 | 对生成产物做 Schema 校验 |

---

## 7. CLAUDE.md 配置最佳实践

**应包含：**
- 构建与测试命令（Claude 无法猜测）
- 项目特有的代码风格规则
- 架构决策与环境特殊性
- 常见的陷阱与非直观行为
- 关键规则使用 `**重要**` 或 `**YOU MUST**` 标记

**不应包含：**
- 标准语言惯例（Claude 已掌握）
- 详细的 API 文档（用链接代替）
- 频繁变化的信息
- 文件级的代码描述

**配置层级：**

```
~/.claude/CLAUDE.md                    # 用户级默认规则
./CLAUDE.md                            # 项目根规则（团队共享）
./packages/api/CLAUDE.md               # 嵌套子目录规则
```

---

## 8. 常见错误与解决方案

| 错误 | 解决方案 |
|------|----------|
| Skill 描述过于宽泛导致误触发 | 缩减到精确的用例，添加 NOT 条件 |
| SKILL.md 过于庞大 | 保持 ≤ 500 行，参考资料移到 references/ |
| 没有输出契约 | 定义 JSON Schema 输出格式 |
| 缺乏治理 | 添加审批钩子，记录每次调用 |
| 跳过测试 | 添加评估用例和回归测试套件 |
| 忽略成本 | 设置预算，监控 Token、延迟 |
| 规则不解释原因 | 每条规则加 WHY 注释 |
| 两次以上犯同样错误 | 运行 `/clear` 后用更好的 prompt 重新开始 |

---

## 9. 资源汇总

### 官方资源

| 资源 | 链接 |
|------|------|
| Claude Code 官方仓库 | [github.com/anthropics/claude-code](https://github.com/anthropics/claude-code) |
| Claude Code 官方文档 | [docs.claude.com/code](https://docs.claude.com/code) |
| Agent SDK 文档 | [code.claude.com/docs/en/agent-sdk](https://code.claude.com/docs/en/agent-sdk/skills) |
| Agent Skills 工程博客 | [claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills](https://claude.com/blog/equipping-agents-for-the-real-world-with-agent-skills) |
| 官方 Skills 仓库 | [github.com/anthropics/skills](https://github.com/anthropics/skills) |
| 工具参考 | [code.claude.com/docs/tools-reference](https://code.claude.com/docs/en/tools-reference) |
| 安全指南 | [code.claude.com/docs/security](https://code.claude.com/docs/en/security) |
| Managed Agents Skills（中文） | [platform.claude.com/docs/zh-CN/managed-agents/skills](https://platform.claude.com/docs/zh-CN/managed-agents/skills) |

### 社区资源

| 资源 | 说明 |
|------|------|
| [claude-code-chinese/claude-code-guide](https://github.com/claude-code-chinese/claude-code-guide) | 中文入门指南（2026 最新） |
| [aman-bhandari/claude-code-agent-skills-framework](https://github.com/aman-bhandari/claude-code-agent-skills-framework) | 15 规则文件 + 21 个 Skills 的 Agent 框架 |
| [shanraisshan/claude-code-best-practice](https://github.com/shanraisshan/claude-code-best-practice) | 天气系统案例：Command → Agent → Skill 三层架构 |
| [DeepLearning.AI 课程](https://corporate.deeplearning.ai/courses/agent-skills-with-anthropic/) | Agent Skills with Anthropic |
| 七牛云 Claude Code 实战 | [news.qiniu.com](https://news.qiniu.com/archives/post-1770253891228-0) |
| 阿里云 Agent Skills 实践 | [developer.aliyun.com/article/1693119](https://developer.aliyun.com/article/1693119) |
| Zilliz Blog: Skills vs MCP | [zilliz.com.cn](https://zilliz.com.cn/blog/Why-Skills-beat-MCP-with-Milvus-knowledge-base) |

### 建议学习路径

1. **入门** — 阅读中文指南 + 创建一个最简单的 Skill（如 timestamp）
2. **进阶** — 学习 SKILL.md 高级字段 + 添加 references/ 和 scripts/
3. **实战** — 开发一个完整的 NL2SQL 或内容生成 Skill
4. **部署** — 通过 Managed Agents API 部署到生产环境
5. **治理** — 添加监控、审批门控、版本管理

---

> **参考来源：** Anthropic 官方博客及文档、Claude Code 官方 GitHub、skywork.ai、GitHub 社区框架（aman-bhandari、claude-code-chinese）、Paradime、Morph、Verdent、阿里云开发者社区、Zilliz 等 — 全部信息截至 2026 年 5 月。
