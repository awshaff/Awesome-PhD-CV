#!/usr/bin/env python3
"""Render all three CV templates from the single source of truth, cv-data.yaml.

Usage:
    python3 generate_cvs.py

Edit cv-data.yaml, re-run this script, then compile each CV as usual
(pdflatex/xelatex/latexmk in its own directory). Content that is unique to
one template (research-cv's grant list, publications, teaching, committees,
etc.) is not touched by this script -- it stays hand-authored.
"""
import pathlib
import yaml
from jinja2 import Environment, FileSystemLoader

ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATES_DIR = ROOT / "templates"

# Maps template file -> generated output file.
OUTPUTS = {
    "jakes-resume.tex.j2": "jakes-format/resume.tex",
    "deedy-resume.tex.j2": "deedy-format/resume.tex",
    "research-cv.tex.j2": "research-cv/cv.tex",
    "research-cv-education.tex.j2": "research-cv/cv/education.tex",
    "research-cv-work_experience.tex.j2": "research-cv/cv/work_experience.tex",
    "research-cv-honors.tex.j2": "research-cv/cv/honors.tex",
}


def githubstars(repo, style="k"):
    """Render `\\href{url}{Name} \\githubstars{N}` for a repo dict."""
    count = repo.get("stars_k") if style == "k" else repo.get("stars_comma")
    count = count or str(repo["stars"])
    return r"\href{%s}{%s} \githubstars{%s}" % (repo["url"], repo["name"], count)


def main():
    with open(ROOT / "cv-data.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    repos_by_key = {r["key"]: r for r in data["repos"]}
    data["repos_by_key"] = repos_by_key
    data["portfolio_repos"] = [r for r in data["repos"] if "portfolio_description" in r]

    for job in data["experience"]:
        keys = job.get("resume_github_repos")
        if keys:
            job["resume_github_list"] = ", ".join(githubstars(repos_by_key[k]) for k in keys)

    industry_honors = [h for h in data["honors"] if h.get("industry_highlight")]
    data["industry_honors_text"] = " \\\\\n     ".join(
        r"\textbf{%s} -- %s" % (h["year"], h["industry_line"]) for h in industry_honors
    )
    data["industry_honors_table"] = "\n".join(
        r"%s & %s \\" % (h["year"], h["industry_line"]) for h in industry_honors
    )

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
    )
    for template_name, output_rel in OUTPUTS.items():
        template = env.get_template(template_name)
        rendered = template.render(**data)
        if not rendered.endswith("\n"):
            rendered += "\n"
        out_path = ROOT / output_rel
        out_path.write_text(rendered, encoding="utf-8")
        print(f"generated {output_rel}")


if __name__ == "__main__":
    main()
