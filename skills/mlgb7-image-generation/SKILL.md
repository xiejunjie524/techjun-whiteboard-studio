---
name: mlgb7-image-generation
description: 通过 MLGB7 OpenAI 兼容图片接口生成或编辑图片。用户要求使用 test.mlgb7.com、MLGB7、OpenAI Images API、gpt-image-2，或需要将提示词输出为本地 PNG/JPEG 时使用。
---

# MLGB7 生图

使用 `scripts/generate_image.py` 调用 `https://test.mlgb7.com/v1/images/generations`，生成图片并保存到本地。API 密钥只能从环境变量 `MLGB7_API_KEY` 或 `~/.codex/mlgb7.env` 读取，严禁写入代码、日志、提交或回复。

## 快速使用

```powershell
python scripts/generate_image.py --prompt "一张极简产品海报" --model gpt-image-2 --size 1024x1024 --out output.png
```

支持 `--prompt`、`--model`、`--size`、`--out`、`--retries` 和 `--base-url`。默认模型为 `gpt-image-2`，默认接口地址为 `https://test.mlgb7.com/v1`。

## 准则

- 生图前确认提示词、画幅和输出路径；视频分镜优先使用无文字、统一画风提示词。
- 解析响应中的 `b64_json` 或 `url`，下载并验证文件大小和图片格式后再交付。
- 网络错误、HTTP 4xx/5xx 和无效响应自动重试；不要打印 Authorization 头或密钥。
- 需要编辑图片时，当前接口技能只承诺 generations；若服务明确支持 edits，再扩展脚本，不要伪造兼容性。

## Structuring This Skill

[TODO: Choose the structure that best fits this skill's purpose. Common patterns:

**1. Workflow-Based** (best for sequential processes)
- Works well when there are clear step-by-step procedures
- Example: DOCX skill with "Workflow Decision Tree" -> "Reading" -> "Creating" -> "Editing"
- Structure: ## Overview -> ## Workflow Decision Tree -> ## Step 1 -> ## Step 2...

**2. Task-Based** (best for tool collections)
- Works well when the skill offers different operations/capabilities
- Example: PDF skill with "Quick Start" -> "Merge PDFs" -> "Split PDFs" -> "Extract Text"
- Structure: ## Overview -> ## Quick Start -> ## Task Category 1 -> ## Task Category 2...

**3. Reference/Guidelines** (best for standards or specifications)
- Works well for brand guidelines, coding standards, or requirements
- Example: Brand styling with "Brand Guidelines" -> "Colors" -> "Typography" -> "Features"
- Structure: ## Overview -> ## Guidelines -> ## Specifications -> ## Usage...

**4. Capabilities-Based** (best for integrated systems)
- Works well when the skill provides multiple interrelated features
- Example: Product Management with "Core Capabilities" -> numbered capability list
- Structure: ## Overview -> ## Core Capabilities -> ### 1. Feature -> ### 2. Feature...

Patterns can be mixed and matched as needed. Most skills combine patterns (e.g., start with task-based, add workflow for complex operations).

Delete this entire "Structuring This Skill" section when done - it's just guidance.]

## [TODO: Replace with the first main section based on chosen structure]

[TODO: Add content here. See examples in existing skills:
- Code samples for technical skills
- Decision trees for complex workflows
- Concrete examples with realistic user requests
- References to scripts/templates/references as needed]

## Resources (optional)

Create only the resource directories this skill actually needs. Delete this section if no resources are required.

### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
