# 华宇元典法律数据 · 检索工具速查

> 均为「华宇元典法律数据」MCP（yuandian-mcp）工具。启用方式：连接器管理页信任 `yuandian-mcp`。
> 查余额：`yuandian_get_user_balance`；看接口清单：`yuandian_list_apis`；查接口文档：`yuandian_get_api_doc`。

## 1. 法条检索：yuandian_law_vector_search
按自然语言 query 做**法条级语义检索**。结果在 `extra.fatiao`（每条=一条法条，非整部法规全文）。

参数：
- `query`（必填）：检索问题/文本。
- `rewrite_flag`（选填，默认 true）：是否对 query 做改写。
- `return_num`（选填，默认 45）：返回条数。
- `fatiao_filter`（选填）：
  - `sxx`：时效性数组，可选：现行有效 / 失效 / 已被修改 / 部分失效 / 尚未生效。**实务默认建议只取「现行有效」。**
  - `effect1`：一级效力级别数组，如 宪法 / 法律 / 司法解释 / 行政法规 / 部门规章 / 地方性法规 等。
  - `law_start` / `law_end`：实施日期范围 YYYY-MM-DD。

返回字段（fatiao 每条）：`fgtitle`(法规名) `num`(第X条) `content`(法条内容) `sxx`(时效性) `effect1`/`effect2`(效力级别) `start`/`end`(实施/失效日期,YYYYMMDD数字) `url`(官方原文链接) `score`(相关度) `fgid`(法规ID,可取法规详情)。

## 2. 类案检索：yuandian_case_vector_search
按自然语言 query 做**案例语义相似检索**（默认覆盖普通+权威案例）。结果在 `extra.wenshu`。

参数：
- `query`（必填）、`rewrite_flag`（默认 true）、`return_num`（默认 45）。
- `wenshu_filter`（选填）：
  - `wenshu_type`：案件类别（刑事案件/民事案件/行政案件/执行案件/…）。
  - `ay`：案由数组（完整案由名，如 买卖合同纠纷、民间借贷纠纷）。
  - `fayuan`：法院数组（完整法院名）。
  - `cj`：法院层级（基层/中级/高级/最高）。
  - `xzqh_p` / `xzqh_c`：省 / 地级市。
  - `ja_start` / `ja_end`：结案日期范围 yyyy-MM-dd。
  - `dianxing`：true=仅权威案例库。
  - `source`：权威案例来源（典型案例/参考案例/公报案例/指导性案例/…）。
  - `wszl`：文书种类编码数组。

返回字段（wenshu 每条）：`title`(案件名) `ah`(案号) `jbdw`(经办法院) `cj`(层级) `spcx`(审级,如二审案件) `jaDate`(结案日期) `anyou`/`ay`(案由) `content`(案情/裁判要旨整理) `db`(所属案例库) `url`(官方链接) `score`(相似度)。

## 3. 其他可用（企业尽调，rh_* 系列）
天眼查式企业信息：`yuandian_rh_enterpriseBaseInfo`(工商) `yuandian_rh_enterpriseWritList`(裁判文书) `yuandian_rh_enterpriseExecutions`(被执行) `yuandian_rh_enterprisePatent`/`Brand`/`Icp` 等——出海合规/尽调场景可用。

## 使用注意
- 法条时效性以 `sxx` 为准；正式引用前用 `url` 复核最新有效版本。
- 检索消耗积分，`return_num` 按需设置（法条常取 5–8，类案 3–5 即可）。
- `content` 是整理后的内容，不等于裁判文书逐字全文；需全文再走详情接口。
