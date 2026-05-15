# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository is a research/learning workspace focused on Claude Code agent development and MCP (Model Context Protocol). It contains:

- **`Claude_Code_智能体与Skill开发部署指南.md`** — A comprehensive Chinese-language guide covering Claude Code Skill development, Harness Engineering, Agent SDK, and deployment strategies (compiled 2026-05-15).
- **`gen_mcp_doc.py`** — A Python script that generates a Chinese-language MCP introduction document as a .docx file.
- **`MCP_Model_Context_Protocol_介绍.docx`** — The generated output from `gen_mcp_doc.py`.

## Commands

- **Generate MCP docx**: `python /f/python3.12.6/python gen_mcp_doc.py` (uses python-docx library)

## Dependencies

- `gen_mcp_doc.py` requires the `python-docx` package: `pip install python-docx`

## Architecture Notes

- The `.claude/settings.local.json` currently has minimal permissions configured (WebSearch and a specific Python binary path).
- The markdown guide is a self-contained reference manual — it is not consumed programmatically by any code in this repo.
- The Python script uses `python-docx` to programmatically create Word documents with styled headings, tables, code blocks, and bullet lists.
