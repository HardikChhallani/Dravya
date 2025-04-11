"""
UI module for the Medicine Finder tab.
"""
import streamlit as st
import re
from src.services.groq_services import groq_service

def parse_medicine_info(response_text):
    """
    Parse medicine information into structured sections.
    
    Args:
        response_text (str): Raw response text from LLM
        
    Returns:
        dict: Structured information by section
    """
    sections = {}
    current_section = "General Information"
    section_content = []
    
    for line in response_text.split('\n'):
        if line.startswith('##'):
            # Save the previous section
            if section_content:
                sections[current_section] = '\n'.join(section_content)
                section_content = []
            # Start a new section
            current_section = line.strip('# ')
        elif line.startswith('#') and len(line.split()) > 1:
            # This is a title, not a section
            continue
        else:
            section_content.append(line)
    
    # Save the last section
    if section_content:
        sections[current_section] = '\n'.join(section_content)
    
    return sections

def show_medicine_finder_tab():
    """Display the medicine finder tab UI and handle interactions."""
    st.header("Find Your Medicines")
    
    st.markdown("""
    Need detailed information about a specific medication? 
    Enter a medication name below to learn about its uses, dosage, side effects, and more.
    """)
    
    # User input
    med_name = st.text_input("Enter medication name:", key="finder_med_name")
    
    # Optional filters
    col1, col2 = st.columns(2)
    with col1:
        include_dosage = st.checkbox("Include dosage information", value=True)
    with col2:
        include_side_effects = st.checkbox("Include side effects", value=True)
    
    search_specific = st.checkbox("Search for specific information", value=False)
    if search_specific:
        specific_info = st.text_input("What specific information are you looking for?", 
                                      placeholder="e.g., interactions with alcohol, pregnancy category")
    
    # Submit button
    if st.button("Find Medicine Information", key="finder_submit"):
        if med_name:
            with st.spinner("Searching for medicine information..."):
                # Construct the query based on user input
                query = f"Provide detailed information about {med_name}"
                
                if include_dosage:
                    query += ", including dosage guidelines"
                
                if include_side_effects:
                    query += ", common and serious side effects"
                
                if search_specific and specific_info:
                    query += f", with special focus on {specific_info}"
                
                query += ". Structure the response with clear headings for different sections."
                
                # Get response from Groq
                response = groq_service.generate_response(query, "medicine_finder")
                response_text = response["content"]
                
                # Parse the structured response
                sections = parse_medicine_info(response_text)
                
                # Display the structured information
                st.subheader(f"Information for {med_name}")
                
                # Display general information first if available
                if "General Information" in sections:
                    st.markdown(sections["General Information"])
                
                # Create expandable sections for the rest of the information
                for section, content in sections.items():
                    if section != "General Information":
                        with st.expander(f"{section}"):
                            st.markdown(content)
                
                # Add a download button for the information
                st.download_button(
                    label="Download Information as Text",
                    data=response_text,
                    file_name=f"{med_name}_information.txt",
                    mime="text/plain"
                )
        else:
            st.warning("Please enter a medication name.")
    
    # Additional resources
    with st.expander("Additional Resources"):
        st.markdown("""
        For more comprehensive information about medications, consider checking these trusted resources:
        
        - [U.S. Food & Drug Administration (FDA)](https://www.fda.gov/)
        - [National Library of Medicine - MedlinePlus](https://medlineplus.gov/)
        - [WebMD](https://www.webmd.com/)
        - [Mayo Clinic](https://www.mayoclinic.org/)
        
        Always consult with a healthcare professional before making decisions about your medication.
        """)