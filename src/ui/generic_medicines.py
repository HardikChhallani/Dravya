"""
UI module for the Generic Medicines tab.
"""
import streamlit as st
import pandas as pd
import re
from src.services.groq_services import groq_service

def extract_pricing_table(text):
    """
    Extract pricing table data from markdown text.
    
    Args:
        text (str): Markdown text containing pricing table
        
    Returns:
        DataFrame or None: Pandas DataFrame if table found, None otherwise
    """
    # Find markdown tables in the text
    table_pattern = r'\|(.+)\|[\r\n]+\|([-:]+\|)+([\r\n]+\|(.+)\|)+'
    table_match = re.search(table_pattern, text)
    
    if table_match:
        table_text = table_match.group(0)
        lines = table_text.strip().split('\n')
        
        # Extract headers
        headers = [h.strip() for h in lines[0].strip('|').split('|')]
        
        # Skip the separator line
        data_rows = lines[2:]  # Skip header and separator
        
        # Extract data
        data = []
        for row in data_rows:
            values = [cell.strip() for cell in row.strip('|').split('|')]
            # Ensure all rows have the same number of columns as headers
            while len(values) < len(headers):
                values.append("")
            data.append(values[:len(headers)])  # Truncate if too many values
            
        return pd.DataFrame(data, columns=headers)
    
    return None

def format_generic_response(response_text):
    """
    Format the generic medicines response for better UI display.
    
    Args:
        response_text (str): Raw response text from LLM
        
    Returns:
        tuple: (DataFrame or None, dict)
    """
    # Try to extract table data
    df = extract_pricing_table(response_text)
    
    # Extract sections
    sections = {}
    current_section = "Overview"
    section_text = []
    
    lines = response_text.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('##'):
            # Save previous section
            if section_text:
                sections[current_section] = '\n'.join(section_text)
            # Start new section
            current_section = line.strip('# ')
            section_text = []
        elif line.startswith('#') and len(line.split()) > 1:
            # Main title - skip
            continue
        elif '|' in line and i < len(lines) - 1 and '|' in lines[i+1] and '-' in lines[i+1]:
            # This is part of a table, skip it to avoid duplication
            continue
        else:
            section_text.append(line)
    
    # Add the last section
    if section_text:
        sections[current_section] = '\n'.join(section_text)
    
    # If no sections were found, put everything in the overview
    if not sections:
        sections["Overview"] = response_text
    
    return df, sections

def show_generic_medicines_tab():
    """Display the generic medicines tab UI and handle interactions."""
    st.header("Generic Medicine Information")
    
    st.markdown("""
    Looking for generic alternatives to brand-name medications? Enter a medication 
    name below to learn about generic options, cost savings, and important information.
    """)
    
    # User input
    med_name = st.text_input("Enter brand-name medication:", key="gen_med_name")
    
    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        include_pricing = st.checkbox("Include pricing information", value=True)
    with col2:
        include_differences = st.checkbox("Show differences from brand-name", value=True)
    
    # Submit button
    if st.button("Find Generic Options", key="gen_submit"):
        if med_name:
            with st.spinner("Searching for generic alternatives..."):
                # Construct the query
                query = f"Provide information about generic alternatives for {med_name}"
                
                if include_pricing:
                    query += ", including pricing comparison"
                
                if include_differences:
                    query += ", any differences in efficacy or side effects"
                
                query += ". Format as a structured response with clear headings and a pricing comparison table if possible."
                
                # Get response from Groq
                try:
                    response = groq_service.generate_response(query, "generic_medicines")
                    response_text = response["content"]
                    
                    # Format the response
                    df, sections = format_generic_response(response_text)
                    
                    # Display the response
                    st.subheader(f"Generic Alternatives for {med_name}")
                    
                    # Display pricing table if found
                    if df is not None and include_pricing:
                        st.markdown("### Price Comparison")
                        st.dataframe(df, use_container_width=True)
                    
                    # Display sections in expanders
                    for title, content in sections.items():
                        if content.strip():
                            with st.expander(f"{title}", expanded=(title == "Overview")):
                                st.markdown(content)
                    
                    # Add a download button for the information
                    st.download_button(
                        label="Download Information as Text",
                        data=response_text,
                        file_name=f"{med_name}_generic_info.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.info("Please try again with a different medication name or check your connection.")
        else:
            st.warning("Please enter a medication name.")
    
    # Educational section about generics
    with st.expander("About Generic Medications"):
        st.markdown("""
        ### What are Generic Medications?
        
        Generic medicines are copies of brand-name medications that have the same:
        - Active ingredients
        - Dosage form
        - Safety profile
        - Strength
        - Route of administration
        - Intended use
        
        ### FDA Requirements for Generic Medications
        
        For a generic medicine to be approved by the FDA, it must:
        - Contain the same active ingredients as the brand-name drug
        - Be identical in strength, dosage form, and route of administration
        - Have the same use indications
        - Meet the same batch requirements for identity, strength, purity, and quality
        - Be manufactured under the same strict standards of FDA's good manufacturing practice regulations
        
        ### Why are Generic Medicines Less Expensive?
        
        Generic medicines are typically less expensive because the manufacturers:
        - Don't have the initial research and development costs
        - Don't need to repeat costly clinical trials
        - Often compete with multiple other generic versions of the same drug
        
        This competition helps lower prices for consumers.
        """)