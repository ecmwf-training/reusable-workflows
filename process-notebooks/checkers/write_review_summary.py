#!/usr/bin/env python3

"""Generate the notebook QA markdown summary table for GitHub Actions."""

from __future__ import annotations

import os
from pathlib import Path


def format_status(result: str) -> str:
    mapping = {
        "success": "Pass",
        "failure": "Fail",
        "cancelled": "Cancelled",
        "skipped": "Skipped",
    }
    return mapping.get(result, "N/A")


def check_status(step_result: str, job_result: str) -> str:
    if not step_result and job_result != "success":
        step_result = job_result
    return format_status(step_result)


def aggregate_status(results: list[str], lint_job_result: str) -> str:
    has_success = False
    has_skipped = False
    has_cancelled = False

    for result in results:
        if result == "failure":
            return "Fail"
        if result == "cancelled":
            has_cancelled = True
        elif result == "success":
            has_success = True
        elif result == "skipped":
            has_skipped = True

    if has_cancelled:
        return "Cancelled"
    if has_success:
        return "Pass"
    if has_skipped:
        return "Skipped"
    if lint_job_result != "success":
        return format_status(lint_job_result)
    return "N/A"


def append_row(rows: list[str], include_all: bool, *columns: str) -> None:
    """Record a table row, filtering to failures unless include_all is set."""
    if include_all or columns[4] == "Fail":
        rows.append("| " + " | ".join(columns) + " |")


def main() -> int:
    env = os.environ

    lint_job_result = env.get("LINT_JOB_RESULT", "")
    execute_job_result = env.get("EXECUTE_JOB_RESULT", "")

    links_status = check_status(env.get("LINK_RESULT", ""), lint_job_result)
    license_status = check_status(env.get("LICENSE_RESULT", ""), lint_job_result)
    metadata_status = check_status(env.get("METADATA_RESULT", ""), lint_job_result)
    data_source_status = check_status(env.get("DATA_SOURCE_RESULT", ""), lint_job_result)
    execute_status = check_status(env.get("EXECUTE_RESULT", ""), execute_job_result)
    code_style_status = aggregate_status(
        [
            env.get("LINTER_RESULT", ""),
            env.get("FORMATTER_RESULT", ""),
            env.get("PYNBLINT_RESULT", ""),
        ],
        lint_job_result,
    )
    tests_status = check_status(env.get("TEST_RESULT", ""), lint_job_result)
    figure_status = check_status(env.get("FIGURE_RESULT", ""), lint_job_result)
    accessibility_status = check_status(env.get("ACCESSIBILITY_RESULT", ""), lint_job_result)
    changelog_status = check_status(env.get("CHANGELOG_RESULT", ""), lint_job_result)

    summary_file = env.get("SUMMARY_FILE")
    if not summary_file:
        summary_file = str(Path(env.get("RUNNER_TEMP", "/tmp")) / "notebook-qa-summary.md")

    include_all = env.get("SUMMARISE_ALL_CHECKS", "").strip().lower() in ("true", "1", "yes")

    rows: list[str] = []

    append_row(rows, include_all, "1. Learning Resource Management", "Reliable access<br>Access to the learning resource and all corresponding information must be open, free, and reliable.", "All links in the learning resource must work.", "1.2.3", links_status, "", "")
    append_row(rows, include_all, "1. Learning Resource Management", "Reliable access<br>Access to the learning resource and all corresponding information must be open, free, and reliable.", "All licences applicable to the learning resource must be provided.", "1.2.4", license_status, "", "")
    append_row(rows, include_all, "1. Learning Resource Management", "Reliable access<br>Access to the learning resource and all corresponding information must be open, free, and reliable.", "The date of the most recent version of the learning resource must be stated.", "1.2.6", metadata_status, "", "")
    append_row(rows, include_all, "1. Learning Resource Management", "Reliable access<br>Access to the learning resource and all corresponding information must be open, free, and reliable.", "The date of the most recent execution of the learning resource code must be stated.", "1.2.7", "N/A", "", "")
    append_row(rows, include_all, "1. Learning Resource Management", "Reliable access<br>Access to the learning resource and all corresponding information must be open, free, and reliable.", "All datasets used in the learning resource must be available.", "1.2.8", data_source_status, "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "All code cells must be able to run sequentially without errors.", "2.2.1", execute_status, "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "All Python code must adhere to the Black style.", "2.2.3", code_style_status, "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "All installation/execute instructions must be functional across current devices and operating systems.", "2.2.4", execute_status, "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "All installation/execute instructions must be functional across current internet browsers.", "2.2.5", "N/A", "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "The learning resource must be functional using the supplied dependencies and/or environment.", "2.3.1", execute_status, "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "All dependencies of the source code must be stable and reliable.", "2.2.8", "N/A", "", "")
    append_row(rows, include_all, "2. Technical Quality", "Code Functionality<br>The code must function as intended, comply with relevant standards, and be user friendly.", "All dependencies of the source code must be regularly security checked.", "2.2.7", "N/A", "", "")
    append_row(rows, include_all, "2. Technical Quality", "Performance<br>The learning resource must be responsive.", "The learning resource must come with a set of tests for evaluating its performance.", "2.3.1", tests_status, "", "")
    append_row(rows, include_all, "2. Technical Quality", "Performance<br>The learning resource must be responsive.", "Performance tests must pass with X% coverage.", "2.3.2", tests_status, "", "")
    append_row(rows, include_all, "3. User Experience", "Accessibility<br>The learning resource must comply with accessibility standards.", "Key text-based information must be compatible with text to audio software.", "3.1.3", accessibility_status, "", "")
    append_row(rows, include_all, "3. User Experience", "Interpretation<br>The learning resource must maintain scientific integrity.", "Graphs and figures must be properly labelled and include source information.", "3.3.2", figure_status, "", "")
    append_row(rows, include_all, "4. Documentation", "Scientific Basis and Value<br>Documentation on the scientific basis and value of the learning resource must be available.", "Underlying sources, datasets, and publications must be referenced.", "4.1.1", "N/A", "", "")
    append_row(rows, include_all, "4. Documentation", "Scientific Basis and Value<br>Documentation on the scientific basis and value of the learning resource must be available.", "All figures, tables, and datasets must be accompanied by appropriate attribution and explanations.", "4.1.2", "N/A", "", "")
    append_row(rows, include_all, "4. Documentation", "Quality Control<br>Quality control and validation activities must be fully documented.", "A record of all revisions and updates must be available in the documentation.", "4.2.3", changelog_status, "", "")
    append_row(rows, include_all, "5. Fitness for Purpose and Scientific Soundness", "In expert reviews only", "N/A", "N/A", "N/A", "N/A", "N/A")

    lines: list[str] = ["## AUTOMATED REVIEW", ""]
    if rows:
        lines.append("| Category | Requirement | Criterion | Ref no.<br>(to be deleted) | Automated Result<br>(to be copied from GH Actions) | Final Verdict from QTO | Note from QTO (if any)<br>e.g., details why final verdict is different: overwritten / not necessary / fail is acceptable |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        lines.extend(rows)
    else:
        lines.append("All automated checks passed. No failures to report.")

    Path(summary_file).write_text("\n".join(lines) + "\n", encoding="utf-8")

    github_output = env.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as handle:
            handle.write(f"summary_file={summary_file}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())