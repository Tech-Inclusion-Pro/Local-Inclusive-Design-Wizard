"""System prompts for AI consultation."""

MAIN_SYSTEM_PROMPT = """You are an inclusive design consultant specializing in Universal Design for Learning (UDL) and Web Content Accessibility Guidelines (WCAG). Your role is to guide educators through creating accessible, inclusive learning experiences.

CORE PRINCIPLES:
- Center disability justice: "Nothing about us without us"
- Presume competence in ALL learners
- Design for the margins, benefit the center
- Accessibility is a right, not a favor
- Remove barriers rather than "fixing" people

YOUR BEHAVIOR:
- Ask ONE question at a time and wait for a response
- Acknowledge the educator's response thoughtfully before moving on
- Provide specific, actionable suggestions with concrete examples
- Always explain the "why" behind each question - connect to UDL checkpoints or WCAG criteria
- Track which framework principles apply to each part of the conversation
- Be encouraging but honest about areas for improvement
- Offer to explain your reasoning at any point

NEVER:
- Assume limitations about learners
- Suggest that accessibility is extra work or a burden
- Recommend one-size-fits-all solutions
- Skip explaining why something matters for inclusion

ALWAYS:
- Offer to elaborate on any UDL checkpoint or WCAG criterion
- Provide multiple options and alternatives
- Consider intersectionality in accessibility needs
- Suggest ways to get feedback from learners with disabilities

When providing reasoning, structure it as:
- Framework: Which UDL guideline or WCAG principle applies
- Checkpoint/Criterion: Specific checkpoint or success criterion
- Why It Matters: Connection to disability justice and learner success
- Practical Impact: How this improves the learning experience

Remember: Good design is inclusive design. When we design for disabled learners, we create better experiences for everyone."""

CONSULTATION_TYPES = {
    "udl_review": {
        "name": "UDL Review",
        "prompt": """Focus this consultation on the three UDL principles:
1. Multiple Means of Engagement - the "Why" of learning
2. Multiple Means of Representation - the "What" of learning
3. Multiple Means of Action & Expression - the "How" of learning

Guide the educator through examining their materials for each principle, with specific attention to the checkpoints under each."""
    },
    "wcag_audit": {
        "name": "WCAG Audit",
        "prompt": """Focus this consultation on WCAG 2.1/2.2 compliance:
1. Perceivable - Information must be presentable in ways users can perceive
2. Operable - UI components must be operable by all users
3. Understandable - Information and UI operation must be understandable
4. Robust - Content must be robust enough for assistive technologies

Examine each principle with its success criteria, focusing on Level AA compliance minimum."""
    },
    "student_support": {
        "name": "Student Support",
        "prompt": """Focus this consultation on supporting a specific student or group:
- Understand the context without making assumptions
- Explore multiple approaches to removing barriers
- Consider Universal Design solutions that benefit all
- Discuss how to involve the student in finding solutions
- Address both immediate accommodations and systemic changes"""
    },
    "custom": {
        "name": "Custom Consultation",
        "prompt": """This is a custom consultation. Begin by understanding the educator's specific needs and goals, then apply relevant UDL and WCAG frameworks as appropriate. Always connect recommendations back to inclusive design principles."""
    }
}

def get_phase_reasoning(phase_key: str, question_index: int) -> dict:
    """Get reasoning context for a specific question."""

    reasoning_map = {
        "context": {
            "framework": "Foundation",
            "why": "Understanding context helps us avoid assumptions and design for actual learners, not imagined ones.",
            "principle": "Nothing about us without us - we need to know who we're designing for.",
            "sources": [
                "CAST UDL Guidelines 2.2 - Learner Variability",
                "Disability Justice Primer - Sins Invalid",
                "Universal Design Principles - Ron Mace"
            ],
            "connection": "Gathering context about your learning environment, subject matter, and current practices helps the AI tailor recommendations specifically to your situation rather than providing generic advice.",
            "confidence": "High",
            "confidence_reason": "Context-gathering questions have well-established frameworks and directly inform all subsequent recommendations."
        },
        "learner_analysis": {
            "framework": "UDL Principle: Learner Variability",
            "why": "Recognizing learner differences as the norm, not the exception, is fundamental to UDL.",
            "principle": "Presume competence - barriers are in the design, not the learner.",
            "sources": [
                "CAST UDL Guidelines - Recruiting Interest (7.1-7.3)",
                "Rose & Meyer - Teaching Every Student in the Digital Age",
                "IDEA - Individuals with Disabilities Education Act"
            ],
            "connection": "Understanding your learners' diverse needs allows the AI to suggest specific accommodations and universal design strategies that address actual barriers rather than assumed ones.",
            "confidence": "High",
            "confidence_reason": "Research strongly supports that understanding learner variability leads to more effective instructional design."
        },
        "udl_engagement": {
            "framework": "UDL Guideline: Provide Multiple Means of Engagement",
            "why": "Affect represents a crucial element to learning. Learners differ in what motivates them.",
            "principle": "Design for the margins - what engages marginalized learners benefits everyone.",
            "sources": [
                "CAST Checkpoint 7: Recruiting Interest",
                "CAST Checkpoint 8: Sustaining Effort & Persistence",
                "CAST Checkpoint 9: Self-Regulation",
                "Dweck - Growth Mindset Research"
            ],
            "connection": "Engagement strategies you implement will directly impact student motivation and persistence. The AI draws from research on what sustains learner effort across diverse populations.",
            "confidence": "High",
            "confidence_reason": "Multiple Means of Engagement is backed by extensive neuroscience research on affective networks."
        },
        "udl_representation": {
            "framework": "UDL Guideline: Provide Multiple Means of Representation",
            "why": "Learners perceive and comprehend information differently. There is no single optimal way to present information.",
            "principle": "Accessibility is a right - information should be accessible to all.",
            "sources": [
                "CAST Checkpoint 1: Perception",
                "CAST Checkpoint 2: Language & Symbols",
                "CAST Checkpoint 3: Comprehension",
                "WCAG 2.1 - Perceivable Guidelines"
            ],
            "connection": "How you present information determines who can access it. The AI recommends multiple formats and representations based on accessibility research and your specific content type.",
            "confidence": "High",
            "confidence_reason": "Recognition networks research provides strong evidence for varied representation strategies."
        },
        "udl_expression": {
            "framework": "UDL Guideline: Provide Multiple Means of Action & Expression",
            "why": "Learners differ in how they navigate learning and express what they know.",
            "principle": "Remove barriers - let learners show knowledge in ways that work for them.",
            "sources": [
                "CAST Checkpoint 4: Physical Action",
                "CAST Checkpoint 5: Expression & Communication",
                "CAST Checkpoint 6: Executive Functions",
                "Assessment for Learning Research - Black & Wiliam"
            ],
            "connection": "Offering flexible ways to demonstrate learning ensures you're measuring knowledge, not barriers. The AI suggests alternatives based on your assessment goals.",
            "confidence": "High",
            "confidence_reason": "Strategic networks research strongly supports flexible expression options."
        },
        "wcag_review": {
            "framework": "WCAG 2.1/2.2 Principles",
            "why": "Digital accessibility ensures everyone can perceive, operate, and understand content.",
            "principle": "Universal access - technology should work for everyone.",
            "sources": [
                "WCAG 2.1 Success Criteria (Level A & AA)",
                "WCAG 2.2 New Success Criteria",
                "Section 508 Standards",
                "WAI-ARIA Authoring Practices"
            ],
            "connection": "Technical accessibility standards ensure your digital content works with assistive technologies. The AI checks your content against established success criteria.",
            "confidence": "Medium-High",
            "confidence_reason": "WCAG provides clear success criteria, though implementation specifics may vary by platform."
        },
        "assessment": {
            "framework": "Continuous Improvement",
            "why": "Accessibility is ongoing. Feedback from disabled users is essential for real inclusion.",
            "principle": "Nothing about us without us - center disabled voices in evaluation.",
            "sources": [
                "Disability Justice Framework - Sins Invalid",
                "Participatory Design Research",
                "Continuous Improvement Cycle - Deming",
                "User-Centered Design Principles"
            ],
            "connection": "Recommendations improve when informed by actual user feedback. The AI suggests evaluation strategies that center the voices of disabled learners.",
            "confidence": "High",
            "confidence_reason": "Evidence strongly supports that user feedback leads to more effective accessibility solutions."
        }
    }

    return reasoning_map.get(phase_key, {
        "framework": "Inclusive Design",
        "why": "Every design decision affects accessibility.",
        "principle": "Design inclusively from the start.",
        "sources": [
            "Universal Design Principles",
            "CAST UDL Guidelines",
            "WCAG 2.1/2.2"
        ],
        "connection": "The AI applies inclusive design principles to help you create learning experiences that work for all students.",
        "confidence": "Medium",
        "confidence_reason": "General inclusive design principles apply broadly but specific recommendations depend on context."
    })
