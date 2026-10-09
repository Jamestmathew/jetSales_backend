import re


def clean_text(text: str) -> str:
    """
    Clean text extracted from a PDF before chunking.

    The goal is to remove PDF extraction noise while preserving
    the actual meaning and structure of the document.
    """

    # Normalize line endings
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    # Remove excessive spaces around line breaks
    text = re.sub(r"[ \t]+\n", "\n", text)

    # Fix common PDF extraction issue where words are joined
    # with no space after punctuation.
    text = re.sub(r"([.!?,:;])([A-Za-z])", r"\1 \2", text)

    # Normalize multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Fix common merged-word patterns found in the JetIntel PDF.
    replacements = {
        "Makingbusiness": "Making business",
        "bringstogether": "brings together",
        "withintelligence": "with intelligence",
        "businessand": "business and",
        "technologyand": "technology and",
        "organizationsgenerate": "organizations generate",
        "informationeasier": "information easier",
        "thinkthrough": "think through",
        "Whatproblem": "What problem",
        "tosolve": "to solve",
        "shouldwe": "should we",
        "Whatshould": "What should",
        "Whatwe": "What we",
        "canbe": "can be",
        "Weconsider": "We consider",
        "Weseek": "We seek",
        "Wedo": "We do",
        "Weare": "We are",
        "Wehelp": "We help",
        "Weunderstand": "We understand",
        "whetheran": "whether an",
        "acrossvirtually": "across virtually",
        "supportorganizations": "support organizations",
        "completelynew": "completely new",
        "basedon": "based on",
        "Oursolutions": "Our solutions",
        "differentapproaches": "different approaches",
        "differenttechnologies": "different technologies",
        "businessproblem": "business problem",
        "customerexperiences": "customer experiences",
        "existingoperation": "existing operation",
        "existingsystems": "existing systems",
        "technologyshould": "technology should",
        "one-timeproject": "one-time project",
        "organizationsevolve": "organizations evolve",
        "withwork": "with work",
        "Continuous LearningTechnology": "Continuous Learning Technology",
        "Ourgoal": "Our goal",
        "Webelieve": "We believe",
        "technologythat": "technology that",
        "ratherthan": "rather than",
        "BuildWithPurpose": "Build With Purpose",
        "DeliverValue": "Deliver Value",
        "businessproblem": "business problem",
        "Everyorganization": "Every organization",
        "wouldbe": "would be",
        "We'd": "We'd",
        "Wecan": "We can",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text