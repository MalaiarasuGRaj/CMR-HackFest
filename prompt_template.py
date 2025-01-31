def get_study_material_prompt(topic, extracted_text):
    return f"""
    As an expert educator, generate **comprehensive and in-depth study material** on '{topic}' based on the provided syllabus content. Ensure the material is detailed, well-structured, and engaging. The generated content should strictly align to the syllabus {extracted_text}.
    
    Day-wise Breakdown:

    Day 1: Cover the foundational concepts and introduce the topic with clear explanations of key terms and principles. Use real-world examples to provide context.
    Day 2: Deepen the understanding with a focus on more complex sub-topics or methods. Encourage students to apply these concepts through exercises or activities.
    Day 3: Continue with advanced concepts, case studies, or problem-solving techniques. Review and reinforce concepts from Day 1 and 2.
    Day 4 and onwards: Continue this approach, moving into expert-level content. Ensure a steady progression from basic to advanced understanding, providing a gradual increase in complexity while revisiting earlier concepts.
    The goal is to ensure that by the end of the material, students have a deep and thorough understanding of '{topic}' and can confidently apply the learned concepts to real-life problems and situations.
    
    ### **Structure the Learning Material as Follows:**

    1. **Introduction:**  
       - Provide a thorough overview of the topic.  
       - Explain its significance and real-world relevance.  

    2. **Detailed Explanation of Key Concepts:**  
       - Cover all fundamental and advanced concepts in depth.  
       - Use step-by-step explanations, diagrams (if possible), and examples.  
       - Include necessary formulas, algorithms, or theoretical frameworks.  

    3. **Real-World Applications & Case Studies:**  
       - Describe how the concepts are used in real life.  
       - Provide industry-specific examples and case studies.  

    4. **Step-by-Step Learning Path:**  
       - Guide the learner through an optimal sequence for mastering the topic.  
       - Include prerequisite knowledge and progression recommendations.  

    5. **Common Misconceptions & Pitfalls:**  
       - Address frequently misunderstood aspects of the topic.  
       - Clarify mistakes students often make.  

    6. **Advanced Insights & Future Trends:**  
       - Explore emerging trends, advanced research, and industry applications.  
       - Mention recent developments related to the topic.  

    7. **Summary & Key Takeaways:**  
       - Highlight the most important points.  
       - Reinforce learning with quick revision notes.  
    """
