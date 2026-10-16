# Platform compatibility — research snapshot (2026-10-15)

Core: SKILL.md + Python 3 + OpenCV contrib + NumPy + original image files. A platform's *skill format* support is not a guarantee it can execute Python or inspect image pixel coordinates. A non-code chat experience can guide the user but cannot claim calibrated script output.

| Platform | Skill import/discovery | Full measurement runtime |
| --- | --- | --- |
| ChatGPT | Skills: Create > Upload from computer (skill.zip) | Conditional: needs access to original photo and code-capable execution; permissions/tool availability vary. |
| OpenAI Codex | Agent Skills directory; local/hosted work environment | Conditional: terminal/code execution + OpenCV availability. |
| Claude.ai | Settings > Features: upload custom skill ZIP on eligible plans | Conditional on code execution and image/file access. |
| Claude Code | `~/.claude/skills/scail-photo-scale/` or `<repo>/.claude/skills/scail-photo-scale/` | Conditional: local Python and permitted script execution. |
| Gemini CLI | `~/.gemini/skills/` or `<repo>/.gemini/skills/`, alternatively `.agents/skills/`; `gemini skills install <git-url>` | Conditional on local Python/dependencies/tools. |
| GitHub Copilot agent | `.github/skills/scail-photo-scale/` or `.agents/skills/scail-photo-scale/`; CLI also personal dirs | Conditional: agent runtime and permitted Python / image inputs. Code review is not a suitable photo measurement session. |
| Cursor Agent | `.cursor/skills/scail-photo-scale/` or `.agents/skills/scail-photo-scale/` | Conditional: agent terminal and image-file access; cloud user skills have sync conditions. |

Official sources (verified on date above):
- ChatGPT: https://help.openai.com/en/articles/20001066-skills-in-chatgpt
- OpenAI API/Codex: https://developers.openai.com/api/docs/guides/tools-skills
- Claude: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview
- Gemini CLI: https://geminicli.com/docs/cli/skills/
- GitHub Copilot: https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills
- Cursor: https://cursor.com/docs/skills

No end-to-end measurement execution has been performed on the named platforms; only portable package validation and local Python tests are covered here.
