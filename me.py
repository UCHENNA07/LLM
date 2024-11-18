import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
from dotenv import load_dotenv

load_dotenv()

# Instantiate the OpenAI client
OPENAI_CLIENT = OpenAI()

def add_https_if_missing(url):
    if not url.startswith('https://'):
        url = 'https://' + url
    return url

def scrape_homepage_text(url):
    url = add_https_if_missing(url)

    # Define headers to mimic a browser request
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.RequestException:
        return 'No company text'

    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Extract the cleaned text content
    text_content = soup.get_text(separator=' ')

    # Further clean up the text
    lines = (line.strip() for line in text_content.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text_content = '\n'.join(chunk for chunk in chunks if chunk)

    return text_content


def generate_job_description(url: str, job_role, experienceLevel: str):
    try:
        text_content = scrape_homepage_text(url)
        prompt = f"""
            Below is a text gotten from a company website. With it, create a JSON with the following fields

            - Job Role [key name: job_role] -> This is a string object which is the same as {job_role}
            - Job Description [key name: job_description] -> This is a HTML string object, with minimum of 200 words. The content of this should be generated from the company website text below, \
                and it should fit the {job_role} role, at the {experienceLevel}. \
                This should contain a header about the company embedded in a strong tag\
                a header about the job embedded in a strong tag, a header about key responsibilities embedded in a strong tag, \
                a header about qualifications also embedded in a strong tag, and a header talking about Why Should We hire you also embedded in a strong tag. \
                The entire job description should be embedded in div tags.
                Be dynamic with the names of the headers. Feel free to change it up sometimes.

            - Skills [key name: skills] -> An array of skills tailored to the {job_role} role at the {experienceLevel}, example ['Python', 'React', 'JavaScript', 'R']
            - Company Location [key name: company_location]: This is a string object denoting the company's location. Use 'N/A' if this does not apply
            - Phone Number [key name: phone_number]: This is an integer denoting a phone number gotten from the company website text below. Use '00000' if no number is found
            - Company Size [key name: company_size]: This is an integer denoting number of employees currently working at the company. Use '0' if no number is found.
            - About the Company[key name: about_company]: This is a string giving a brief description of the company.
            - Year Foounded [key name: year_founded]: This is an integer which is the year the company was founded. Use '2000' if no year is found.
            - Industry [key_name: industry]: This is a string object denoting what industry category that the company belongs to. You must pick from one of \
            [Accounting and Finance, Administrative and Office Support, Customer Service, Engineering, Healthcare, Human Resources, Information Technology, Legal, Marketing and Sales,\
            Operations, Retail, Education, Hospitality and Food Service, Manufacturing, Arts and Design, Science and Research, Transportation and Logistics, Construction, Consulting]
            - why_you_should_work_for_us: This is a string object denoting the reasons why a candidate should be hired
            - experienceLevel: This is a string object which is the same as {experienceLevel}

            Company website text:\n
            {text_content}

            Examples of acceptable job descriptions (without HTML tags):
            Example 1 ->
            About the job
            Company Overview: 
            1840 & Company is a global business process outsourcing provider that connects companies with vetted, remote talent across various disciplines. 
            We are dedicated to revolutionizing how companies hire, manage, and grow their workforce in today's dynamic global job market. With our vast network 
            of pre-vetted talent in over 150 countries, we offer solutions that significantly reduce hiring costs and enhance workforce flexibility and efficiency.

            Job Summary: 
            We are seeking an experienced AI Developer to create advanced AI search applications for our diverse range of clients. The ideal candidate will possess 
            a strong background in web crawling and scraping, as well as in developing AI-driven search functionalities for various purposes. This should include 
            specific experience with keyword and semantic searches (both hybrid sparse and dense techniques) and vector databases like Pinecone. Additionally, a 
            solid track record in automating crawling and scraping of large amounts of website data, using tools such as Apify's web crawler, is essential. The role 
            entails extensive web data crawling and scraping, processing and vectorizing this data, and then upserting it into a vector database like Pinecone to 
            create sophisticated AI search functionality. This functionality will then be integrated into APIs for use by front-end developers.

            Key Responsibilities

            - Design and develop advanced AI search functionality using Pinecone for vector storage and OpenAI for enhanced keyword search generation.
            - Automate the process of crawling and scraping web content, ensuring efficient and accurate data collection.
            - Design and implement secure data management protocols to ensure all collected data is saved directly to company-controlled systems, avoiding local storage to maintain data security and availability.
            - Pre-process scraped data to ensure its relevance and readiness for analysis and storage.
            - Vectorize content into embeddings using advanced models such as text-embedding-3-small or ADA v2, ensuring optimal search performance and accuracy.
            - Manage the upserting pipeline to store vectorized content into Pinecone, ensuring seamless data integration and retrieval.
            - Develop and maintain APIs using AWS services, including Lambda for scalability and API Gateway for API management.
            - Work closely with the development team (ReactJS/WordPress) to integrate the AI search functionality onto the front end of website.
            - Utilize FastAPI for developing robust search logic APIs and ensure smooth frontend integration.
            - Collaborate with cross-functional teams to define project scope, plan resources, and ensure timely delivery of projects.
            - Conduct thorough testing and gather feedback to refine and optimize the search tool.
            - Stay abreast of the latest AI and machine learning technologies and methodologies to drive continuous innovation.
            - Exhibit strong self-management skills, capable of independently driving projects forward and delivering results promptly and effectively.

            Qualifications:

            - Bachelor's or Master's degree in Computer Science, Artificial Intelligence, Machine Learning, or related field.
            - Expertise in automating web crawling and scraping, with a deep understanding of circumventing blockers to ensure reliable data collection. Proven 
              ability to optimize processes to reduce the costs associated with crawling and scraping.
            - Proven experience in developing AI-driven search tools, with at least 2+ years of experience working with vector databases, specifically Pinecone.
            - In-depth knowledge of OpenAI GPT-3, including experience with generating keywords and enhancing search functionalities.
            - Strong proficiency in AWS services (Lambda, API Gateway, DynamoDB) and experience with deploying Dockerized applications using AWS Lambda.
            - Experience with FastAPI or similar frameworks for API development.
            - Familiarity with front-end integration and ensuring seamless user experiences.
            - Excellent problem-solving abilities, with a keen attention to detail and a commitment to high-quality output.
            - Strong communication skills and the ability to work collaboratively in a fast-paced, dynamic environment.

            Benefits

            - Work from home
            - Access to diverse projects
            - Opportunities for professional growth
            - Collaboration with diverse teams
            - No commute time
            - No dress code (unless there's a meeting!)
            - Eco-friendly work lifestyle
            - Exposure to a multicultural team
            - Potential for long-term engagement
            - Improved work-life balance

            About 1840 & Company

            1840 & Company is a global leader in Business Process Outsourcing (BPO) and remote talent solutions, dedicated to propelling businesses forward through our 
            comprehensive suite of services. We specialize in connecting companies with world-class freelance professionals and delivering top-tier outsourcing services, 
            across over 150 countries worldwide. Our mission is to empower growth for forward-thinking businesses, seamlessly bridging any skill or resource gaps with 
            our expertly vetted talent pool. We firmly believe in fostering an environment where exceptional individuals can achieve an optimal work-life balance, 
            working remotely from any location, while maximizing their professional growth and earning potential. We are headquartered in Overland Park, KS, USA with 
            service delivery facilities in the Philippines, India, Ukraine, South Africa and Argentina. We invite you to explore the opportunities we offer and consider
            joining our exclusive network of global freelance talent.
            """
        
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4o",
            temperature=0,
            messages=[
            {
                "role":"system",
                "content":"""Given a company website text, a job role and the experience level, you generate only a JSON object"""
            },
            {
                "role": "user", 
                "content": prompt
            }
            ]
        )
        # Find the starting and ending indices of the JSON substring
        start_index = response.choices[0].message.content.find('{')
        end_index = response.choices[0].message.content.rfind('}') + 1

        # Extract the JSON substring
        json_str = response.choices[0].message.content[start_index:end_index]

        try:
            result = json.loads(json_str)
        except:
            raise ValueError()

        return result
        
    except requests.exceptions.Timeout:
        return "The request timed out. Please try again later."
    
    
    except Exception as e:
        # Handle any other unexpected errors
        return f"An unexpected error occurred: {e}"


job_description = generate_job_description(url='https://divverse.com/', job_role='Data Engineer', experienceLevel='Mid Level')
print(job_description)