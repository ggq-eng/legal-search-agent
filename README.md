# legal-search-agent

> 来源分类：**原创/AI打磨** ｜ 导出批次：published

法律检索智能体（对应 C002 FR-06）。输入自然语言法律问题，调用「华宇元典法律数据」MCP 做法条级语义检索与类案检索，返回带官方链接、时效性、效力级别、相似度的结构化检索报告(Markdown/DOCX)。触发词：法律检索、查法条、找类案、法条依据、判例检索、这个问题法律怎么规定、有没有类似判例。

## 安装

把本文件夹整体复制到 WorkBuddy 技能目录：

```bash
cp -r . ~/.workbuddy/skills/legal-search-agent        # 用户级
# 或
cp -r . <项目>/.workbuddy/skills/legal-search-agent   # 项目级
```

重启/刷新 WorkBuddy 后即可在对话中触发。

## 说明

- 本技能从本地 WorkBuddy 环境导出，**所有真实密钥已脱敏为占位符**，使用前请配置你自己的 API Key。
- 若来自技能市场（文件夹名以 `__skillhub` 结尾），版权归原作者，请遵守其许可证。
