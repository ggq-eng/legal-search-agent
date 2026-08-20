# legal-search-agent

> **分类**：原创 / AI 打磨 ｜ **文件数**：7 ｜ **仓库目录**：`legal-search-agent`

## 📌 简介

法律检索智能体（对应 C002 FR-06）。输入自然语言法律问题，调用「华宇元典法律数据」MCP 做法条级语义检索与类案检索，返回带官方链接、时效性、效力级别、相似度的结构化检索报告(Markdown/DOCX)。触发词：法律检索、查法条、找类案、法条依据、判例检索、这个问题法律怎么规定、有没有类似判例。

## 🎯 适用场景

当您有以下需求时可使用本技能（触发词）：法律检索、查法条、找类案、法条依据、判例检索、这个问题法律怎么规定、有没有类似判例。

## 📂 目录结构

```text
  - .gitignore
  - LICENSE
  - README.md
  - SKILL.md
  - **examples/**
    - sample_query.json
  - **references/**
    - yuandian_tools.md
  - **scripts/**
    - render_report.py
```

## 🚀 安装方法

将本文件夹整体复制到 WorkBuddy 的技能目录即可启用：

```bash
# 用户级（推荐）
cp -r . ~/.workbuddy/skills/legal-search-agent

# 或项目级
cp -r . <你的项目>/.workbuddy/skills/legal-search-agent
```

复制完成后，**重启或刷新 WorkBuddy**，即可在对话中用自然语言触发该技能。

## ⚙️ 配置说明

本技能开箱即用，**无需额外配置**。若涉及外部 API 调用，请在使用时按需提供您自己的密钥（不要提交到公开仓库）。

## 📖 使用说明（完整规范）

> 以下为该技能的完整说明，涵盖核心能力、工作流程与关键规则，帮助您全面了解其运作方式。

## 角色
面向律师/法务的法律检索助手。把一句自然语言问题，转成"真实法条依据 + 相关类案"的结构化检索报告，秒级替代人工大海捞针，且每条结论均可溯源到官方原文链接。

## 关键架构（务必理解）
- **真实检索由「华宇元典」MCP 完成**，不是本地脚本臆造：
  - 法条：`yuandian_law_vector_search`（结果在 `extra.fatiao`）
  - 类案：`yuandian_case_vector_search`（结果在 `extra.wenshu`）
- **报告渲染由零依赖脚本完成**：`scripts/render_report.py`（纯标准库，离线、不出域，输出 .md/.docx）。
- 分工清晰：MCP 拿真数据 → Agent 整理成 JSON → 脚本出报告。**法条绝不臆造，无命中就如实说明。**

## 前置条件
- 已在连接器管理页信任并启用 `yuandian-mcp`（华宇元典法律数据）。若未连接，提示用户先启用，不要用离线数据伪造法条。

## 工作流
1. **澄清检索意图**：明确法律问题、（可选）时效性/效力级别/案由/法院/地域/日期等过滤条件。
2. **调法条检索**：`yuandian_law_vector_search`，query=用户问题；可用 `fatiao_filter`（sxx 时效性、effect1 效力级别、law_start/law_end 实施日期）过滤；`return_num` 控制数量。
3. **调类案检索**：`yuandian_case_vector_search`，query=用户问题；可用 `wenshu_filter`（wenshu_type 案件类别、ay 案由、fayuan 法院、xzqh_p/xzqh_c 地域、ja_start/ja_end 结案日期、dianxing 仅权威案例）过滤。
4. **整理为 JSON**：从 `extra.fatiao` / `extra.wenshu` 抽取字段，写成 `input.json`（结构见 `examples/sample_query.json`）。
   - 法条字段：fgtitle, num, content, sxx, effect1, effect2, start, url, score
   - 类案字段：title, ah, jbdw, spcx, jaDate, anyou, content, url, score
5. **渲染报告**：`python render_report.py <input.json> <output_dir> [--docx]`。
6. **回报**：给出核心法条、可参考类案与使用提示，强调"须律师核对最新有效版本"。

## 工具 / 脚本
- `scripts/render_report.py`：JSON → 结构化检索报告（.md + 可选 .docx），零依赖、离线。
  用法：`python render_report.py <input.json> <output_dir> --docx`
- 检索能力：华宇元典 MCP（见 `references/yuandian_tools.md` 速查）。

## 知识
- `references/yuandian_tools.md`：华宇元典检索工具参数与过滤字段速查（法条/类案）。
- `examples/sample_query.json`：真实检索结果示例（公司对外担保效力问题，含九民纪要17/19/22条 + 3篇2025年二审判例）。

## 输出
- `法律检索_<问题摘要>.md`（+ 可选 `.docx`）：含①法条依据 ②相关类案 ③检索小结，每条带官方链接与时效性/相似度。

## 约束 / 合规红线
- 法条与判例**必须来自华宇元典真实检索**，不得用离线示例库或模型记忆臆造。
- 时效性以库内标注为准；引用前须经原文链接复核最新有效版本。
- 报告为 **AI 检索初稿，不构成法律意见**，须经承办律师终审确认后方可用于正式文书。
- 敏感检索内容仅本地处理，报告落盘在企业工作区，数据不出域。

## 验收口径
- 法条 Top-5 与问题相关；命中的法条均带时效性与官方链接。
- 类案带案号/法院/审级/结案日期/相似度，可点链接溯源。
- 无命中时如实标注，不编造。

## ⚠️ 注意事项

- 本技能从本地 WorkBuddy 环境导出，**所有真实密钥 / 凭据 / 个人数据均已脱敏为占位符**，重新使用前请配置您自己的 Key。
- 如为原创技能，可自由使用、修改与再分发；若对外分享请保留作者与来源信息。
- 技能提供的是自动化辅助能力，不替代专业判断；涉及交易、法律、医疗等高风险场景请谨慎并自担风险。

## 📄 许可证

MIT License —— 详见仓库内 `LICENSE` 文件。
