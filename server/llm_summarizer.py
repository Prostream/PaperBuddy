"""
LLM Summarization Module (Module B)

Generates Like-I'm-Five style summaries of academic papers using OpenAI GPT.
Creates kid-friendly explanations with teaching context and glossaries.
Falls back to mock data when API key is unavailable.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional


class LLMSummarizer:
    """Generates kid-friendly academic paper summaries using LLM."""

    def __init__(self, backend="openai"):
        """
        Initialize LLM summarizer.

        Args:
            backend: "openai" or "mock"
        """
        self.backend = backend
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.max_retries = 3
        self.timeout = 60  # seconds

    def summarize(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        sections: List[Dict[str, str]],
        course_topic: str = "CV"
    ) -> Dict[str, Any]:
        """
        Generate Like-I'm-Five summary of academic paper.

        Args:
            title: Paper title
            authors: List of author names
            abstract: Paper abstract
            sections: List of sections with heading and content
            course_topic: "CV" | "NLP" | "Systems"

        Returns:
            Dictionary with summary fields (big_idea, steps, example, etc.)
        """
        try:
            if self.backend == "openai" and self.openai_key:
                return self._summarize_openai(title, authors, abstract, sections, course_topic)
            else:
                print("⚠️  No OpenAI API key found, returning mock summary")
                return self._get_mock_summary(course_topic)
        except Exception as e:
            print(f"LLM summarization failed: {e}")
            print("Falling back to mock summary")
            return self._get_mock_summary(course_topic)

    def _summarize_openai(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        sections: List[Dict[str, str]],
        course_topic: str
    ) -> Dict[str, Any]:
        """Generate summary using OpenAI GPT API."""
        import openai

        client = openai.OpenAI(api_key=self.openai_key)
        prompt = self._build_prompt(title, authors, abstract, sections, course_topic)

        # Retry logic for API calls
        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",  # Use GPT-4o for better JSON adherence
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an expert teacher who explains complex academic papers in simple, kid-friendly language. Always respond with valid JSON."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.7,
                    max_tokens=2000,
                    timeout=self.timeout
                )

                # Parse response
                content = response.choices[0].message.content
                summary = json.loads(content)

                # Validate required fields
                summary = self._validate_and_fix_summary(summary)

                return summary

            except openai.APITimeoutError:
                print(f"Attempt {attempt + 1}/{self.max_retries}: API timeout")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

            except openai.RateLimitError:
                print(f"Attempt {attempt + 1}/{self.max_retries}: Rate limit hit")
                if attempt < self.max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise

            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(1)
                else:
                    raise

            except Exception as e:
                print(f"Attempt {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2)
                else:
                    raise

        # Should not reach here, but just in case
        raise Exception("All retry attempts failed")

    def _build_prompt(
        self,
        title: str,
        authors: List[str],
        abstract: str,
        sections: List[Dict[str, str]],
        course_topic: str
    ) -> str:
        """Build prompt for LLM with Like-I'm-Five instructions."""

        # Build context from sections (limit to avoid token overflow)
        sections_text = ""
        if sections:
            sections_text = "\n\n".join([
                f"## {s['heading']}\n{s['content'][:500]}..."  # Limit each section
                for s in sections[:3]  # Only first 3 sections
            ])

        # Topic-specific context
        topic_contexts = {
            "CV": "computer vision and image understanding",
            "NLP": "natural language processing and text understanding",
            "Systems": "computer systems, networks, and infrastructure"
        }
        topic_context = topic_contexts.get(course_topic, "computer science")

        prompt = f"""You are a teacher explaining a research paper to 5-year-old kids. Be simple, clear, and fun!

**Paper Information:**
- Title: {title}
- Authors: {', '.join(authors)}
- Course Topic: {course_topic} ({topic_context})

**Abstract:**
{abstract}

{sections_text if sections_text else ""}

**Your Task:**
Create a kid-friendly summary in JSON format. Use VERY simple words. Keep sentences SHORT (maximum 12 words each).

**Required JSON Structure:**
{{
  "big_idea": "One sentence explaining the main idea (≤12 words)",
  "steps": [
    "Step 1: Simple description",
    "Step 2: Simple description",
    "Step 3: Simple description"
  ],
  "example": "A real-world example or analogy that a kid would understand",
  "why_it_matters": "Why this research is important for the world",
  "limitations": "What doesn't work well or what problems remain",
  "glossary": [
    {{"term": "Technical Term 1", "definition": "Simple explanation a kid can understand"}},
    {{"term": "Technical Term 2", "definition": "Simple explanation a kid can understand"}}
  ],
  "for_class": {{
    "prerequisites": ["Topic 1 students need to know", "Topic 2 students need to know"],
    "connections": ["How this relates to Topic X", "How this relates to Topic Y"],
    "discussion_questions": [
      "Thought-provoking question 1?",
      "Thought-provoking question 2?"
    ]
  }},
  "accuracy_flags": ["Any uncertainties or things to be careful about"]
}}

**Style Guidelines:**
- Write like you're talking to a 5-year-old
- Use everyday examples (toys, games, animals, food)
- Avoid jargon - if you must use technical terms, explain them in glossary
- Keep it positive and encouraging
- Make it fun and engaging
- Each sentence must be ≤12 words
- Include 3-5 steps in the "steps" array
- Include 3-5 technical terms in glossary
- Include 2-3 prerequisites, connections, and discussion questions each

**Important:** Return ONLY valid JSON, no extra text before or after."""

        return prompt

    def _validate_and_fix_summary(self, summary: Dict[str, Any]) -> Dict[str, Any]:
        """Validate summary has all required fields and fix if needed."""

        # Required fields with defaults
        defaults = {
            "big_idea": "This paper teaches computers to do something smart",
            "steps": [
                "Scientists had a problem to solve",
                "They tried a new way to fix it",
                "They tested if it works well"
            ],
            "example": "Like teaching a computer to recognize your pet",
            "why_it_matters": "This helps make computers smarter and more helpful",
            "limitations": "It doesn't work perfectly in all situations",
            "glossary": [],
            "for_class": {
                "prerequisites": ["Basic understanding of the topic"],
                "connections": ["Relates to other computer science concepts"],
                "discussion_questions": ["How might this be used in real life?"]
            },
            "accuracy_flags": []
        }

        # Fill in missing fields
        for key, default_value in defaults.items():
            if key not in summary or not summary[key]:
                summary[key] = default_value

        # Validate nested for_class structure
        if "for_class" in summary:
            for_class = summary["for_class"]
            if not isinstance(for_class, dict):
                summary["for_class"] = defaults["for_class"]
            else:
                if "prerequisites" not in for_class:
                    for_class["prerequisites"] = defaults["for_class"]["prerequisites"]
                if "connections" not in for_class:
                    for_class["connections"] = defaults["for_class"]["connections"]
                if "discussion_questions" not in for_class:
                    for_class["discussion_questions"] = defaults["for_class"]["discussion_questions"]

        # Ensure glossary is a list of dicts
        if not isinstance(summary.get("glossary"), list):
            summary["glossary"] = []

        # Ensure steps is a list
        if not isinstance(summary.get("steps"), list):
            summary["steps"] = defaults["steps"]

        return summary

    def _get_mock_summary(self, course_topic: str = "CV") -> Dict[str, Any]:
        """Return mock summary when API is unavailable."""

        mock_summaries = {
            "CV": {
                "big_idea": "Computers learn to see like humans do",
                "steps": [
                    "Feed lots of pictures to computer",
                    "Computer finds patterns in pictures",
                    "Computer learns what things look like",
                    "Computer can now recognize new things"
                ],
                "example": "Like teaching a kid to recognize dogs by showing many dog photos",
                "why_it_matters": "Helps self-driving cars see pedestrians and stop signs",
                "limitations": "Gets confused by weird lighting or unusual angles",
                "glossary": [
                    {"term": "Neural Network", "definition": "A computer brain made of many tiny helpers"},
                    {"term": "Training", "definition": "Teaching the computer by showing examples"},
                    {"term": "Dataset", "definition": "A big collection of pictures for learning"}
                ],
                "for_class": {
                    "prerequisites": ["Basic machine learning", "Linear algebra", "Python programming"],
                    "connections": ["Relates to CNNs", "Builds on deep learning", "Used in robotics"],
                    "discussion_questions": [
                        "How is this different from traditional computer vision?",
                        "What are the ethical implications of AI vision?",
                        "Where else could this technology be applied?"
                    ]
                },
                "accuracy_flags": [
                    "⚠️ This is MOCK data - OpenAI API key not configured",
                    "Set OPENAI_API_KEY in .env to get real summaries"
                ]
            },
            "NLP": {
                "big_idea": "Computers learn to understand human language",
                "steps": [
                    "Computer reads lots of text and books",
                    "It learns how words go together",
                    "It understands what sentences mean",
                    "It can talk back in human language"
                ],
                "example": "Like a robot learning to chat by reading many conversations",
                "why_it_matters": "Makes chatbots smarter and helps translate languages",
                "limitations": "Sometimes misunderstands jokes or complex meanings",
                "glossary": [
                    {"term": "Language Model", "definition": "A computer that learned to understand words"},
                    {"term": "Tokenization", "definition": "Breaking sentences into small pieces"},
                    {"term": "Embeddings", "definition": "Numbers that represent word meanings"}
                ],
                "for_class": {
                    "prerequisites": ["Basic NLP concepts", "Probability theory", "Python"],
                    "connections": ["Relates to transformers", "Used in chatbots", "Powers translation"],
                    "discussion_questions": [
                        "How do language models learn meaning?",
                        "What biases might exist in text data?",
                        "Can computers truly understand language?"
                    ]
                },
                "accuracy_flags": [
                    "⚠️ This is MOCK data - OpenAI API key not configured",
                    "Set OPENAI_API_KEY in .env to get real summaries"
                ]
            },
            "Systems": {
                "big_idea": "Making computers work faster and more efficiently",
                "steps": [
                    "Find slow parts in the system",
                    "Design a clever way to speed up",
                    "Build and test the new system",
                    "Measure if it's actually faster"
                ],
                "example": "Like organizing your toys so you find them faster",
                "why_it_matters": "Makes apps load quicker and saves electricity",
                "limitations": "More speed often means more complexity",
                "glossary": [
                    {"term": "Throughput", "definition": "How much work gets done per second"},
                    {"term": "Latency", "definition": "How long you wait for something to happen"},
                    {"term": "Scalability", "definition": "Ability to handle more work without breaking"}
                ],
                "for_class": {
                    "prerequisites": ["Operating systems", "Computer architecture", "Networks"],
                    "connections": ["Relates to distributed systems", "Used in cloud computing"],
                    "discussion_questions": [
                        "What trade-offs exist between speed and reliability?",
                        "How do we measure system performance?",
                        "What are the limits of optimization?"
                    ]
                },
                "accuracy_flags": [
                    "⚠️ This is MOCK data - OpenAI API key not configured",
                    "Set OPENAI_API_KEY in .env to get real summaries"
                ]
            }
        }

        return mock_summaries.get(course_topic, mock_summaries["CV"])
