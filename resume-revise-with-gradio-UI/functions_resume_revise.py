# functions for resume optimization
from openai import OpenAI
from sk import my_sk
from markdown import markdown
from weasyprint import HTML
import os
import pypdf
import markdown


def create_prompt(resume_string: str, jd_string: str) -> str:
    """
    Creates a detailed prompt for AI-powered resume optimization based on a job description.

    This function generates a structured prompt that guides the AI to:
    - Tailor the resume to match job requirements
    - Optimize for ATS systems
    - Provide actionable improvement suggestions
    - Format the output in clean Markdown

    Args:
        resume_string (str): The input resume text
        jd_string (str): The target job description text

    Returns:
        str: A formatted prompt string containing instructions for resume optimization
    """
    return f"""
You are a professional resume optimization expert specializing in tailoring resumes to specific job descriptions. Your goal is to optimize my resume and provide actionable suggestions for improvement to align with the target role.

### Guidelines:
1. **Relevance**:  
   - Prioritize experiences, skills, and achievements **most relevant to the job description**.  
   - Remove or de-emphasize irrelevant details to ensure a **concise** and **targeted** resume.
   - Limit work experience section to 2-3 most relevant roles
   - Limit bullet points under each role to 2-3 most relevant impacts

2. **Action-Driven Results**:  
   - Use **strong action verbs** and **quantifiable results** (e.g., percentages, revenue, efficiency improvements) to highlight impact.  

3. **Keyword Optimization**:  
   - Integrate **keywords** and phrases from the job description naturally to optimize for ATS (Applicant Tracking Systems).  

4. **Additional Suggestions** *(If Gaps Exist)*:  
   - If the resume does not fully align with the job description, suggest:  
     1. **Additional technical or soft skills** that I could add to make my profile stronger.  
     2. **Certifications or courses** I could pursue to bridge the gap.  
     3. **Project ideas or experiences** that would better align with the role.  

5. **Formatting**:  
   - Output the tailored resume in **clean Markdown format**.  
   - Include an **"Additional Suggestions"** section at the end with actionable improvement recommendations.  

---

### Input:
- **My resume**:  
{resume_string}

- **The job description**:  
{jd_string}

---

### Output:  
1. **Tailored Resume**:  
   - A resume in **Markdown format** that emphasizes relevant experience, skills, and achievements.  
   - Incorporates job description **keywords** to optimize for ATS.  
   - Uses strong language and is no longer than **one page**.

2. **Additional Suggestions** *(if applicable)*:  
   - List **skills** that could strengthen alignment with the role.  
   - Recommend **certifications or courses** to pursue.  
   - Suggest **specific projects or experiences** to develop.
"""


def get_resume_response(prompt: str, api_key: str, model: str = "gpt-4o-mini", temperature: float = 0.7) -> str:
    """
    Sends a resume optimization prompt to OpenAI's API and returns the optimized resume response.

    This function:
    - Initializes the OpenAI client
    - Makes an API call with the provided prompt
    - Returns the generated response

    Args:
        prompt (str): The formatted prompt containing resume and job description
        api_key (str): OpenAI API key for authentication
        model (str, optional): The OpenAI model to use. Defaults to "gpt-4-turbo-preview"
        temperature (float, optional): Controls randomness in the response. Defaults to 0.7

    Returns:
        str: The AI-generated optimized resume and suggestions

    Raises:
        OpenAIError: If there's an issue with the API call
    """
    # Setup API client
    client = OpenAI(api_key=api_key)

    # Make API call
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Expert resume writer"},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )

    # Extract and return response
    return response.choices[0].message.content



def is_pdf(filename):
    return filename.lower().endswith('.pdf')

def pdf_to_markdown(pdf_path):
    pdf_reader = pypdf.PdfReader(pdf_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() + "\n"
    md = markdown.markdown(text)
    return md

def read_file(file_path):
    if is_pdf(file_path):
        print("Converting PDF to markdown format...")
        return pdf_to_markdown(file_path)
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()

def process_resume(resume, jd_string):
    """
    Process a resume file against a job description to create an optimized version.

    Args:
        resume (str): Path to the resume file (can be PDF or markdown)
        jd_string (str): The job description text to optimize the resume against

    Returns:
        tuple: A tuple containing three elements:
            - str: The optimized resume in markdown format (for display)
            - str: The same optimized resume (for editing)
            - str: Suggestions for improving the resume
    """
    # Read resume
    resume_string = read_file(resume)

    # Create prompt
    prompt = create_prompt(resume_string, jd_string)

    # Generate response
    response_string = get_resume_response(prompt, my_sk)
    response_list = response_string.split("## Additional Suggestions")
    
    # Extract new resume and suggestions for improvement
    new_resume = response_list[0]
    suggestions = "## Additional Suggestions \n\n" + response_list[1]

    return new_resume, new_resume, suggestions


def export_resume(new_resume):
    """
    Convert a markdown resume to PDF format and save it.

    Args:
        new_resume (str): The resume content in markdown format

    Returns:
        str: A message indicating success or failure of the PDF export
    """
    try:
        # save as PDF
        output_pdf_file = "resumes/resume_new.pdf"
        
        # Convert Markdown to HTML
        html_content = markdown(new_resume)
        
        # Convert HTML to PDF and save
        HTML(string=html_content).write_pdf(output_pdf_file, stylesheets=['resumes/style.css'])

        return f"Successfully exported resume to {output_pdf_file} 🎉"
    except Exception as e:
        return f"Failed to export resume: {str(e)} 💔"