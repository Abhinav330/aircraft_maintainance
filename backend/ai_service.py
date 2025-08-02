import os
import base64
import logging
import re
from openai import AsyncOpenAI
from PIL import Image
import io

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        print(f"=== AI SERVICE INITIALIZATION ===")
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"❌ OPENAI_API_KEY not found in environment variables")
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        print(f"✅ OpenAI API key found")
        self.client = AsyncOpenAI(api_key=api_key)
        print(f"✅ OpenAI client initialized")

    def encode_image_to_base64(self, image_bytes):
        """Convert image bytes to base64 string"""
        print(f"🔄 Encoding image to base64")
        try:
            # Open image with PIL to validate and potentially convert
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes buffer
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG')
            image_bytes = buffer.getvalue()
            
            # Encode to base64
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            print(f"✅ Image encoded to base64: {len(base64_image)} characters")
            return base64_image
            
        except Exception as e:
            print(f"❌ ERROR encoding image: {e}")
            raise e

    def get_system_prompt(self):
        """Read the system prompt from external file"""
        print(f"🔄 Reading system prompt from file")
        try:
            prompt_file_path = os.path.join(os.path.dirname(__file__), "prompts", "maintenance_log_analyzer.txt")
            print(f"📝 Prompt file path: {prompt_file_path}")
            
            if not os.path.exists(prompt_file_path):
                print(f"❌ Prompt file not found: {prompt_file_path}")
                raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")
            
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                prompt = file.read()
                print(f"✅ System prompt loaded: {len(prompt)} characters")
                return prompt
                
        except Exception as e:
            print(f"❌ ERROR reading system prompt: {e}")
            raise e

    async def analyze_maintenance_log(self, image_bytes):
        """Analyze maintenance log image using GPT-4o Vision"""
        print(f"=== AI ANALYSIS START ===")
        try:
            # Encode image
            print(f"🔄 Encoding image to base64")
            base64_image = self.encode_image_to_base64(image_bytes)
            
            # Get system prompt
            print(f"🔄 Getting system prompt")
            system_prompt = self.get_system_prompt()
            
            # Prepare the API call
            print(f"🔄 Preparing OpenAI API call")
            messages = [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please analyze this aircraft maintenance log image and extract the structured data according to the specified format."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            print(f"🔄 Calling OpenAI API with GPT-4o Vision")
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            print(f"✅ OpenAI API call completed")
            print(f"📝 Response usage: {response.usage}")
            
            # Extract the response content
            content = response.choices[0].message.content
            print(f"📝 Raw AI response length: {len(content)} characters")
            print(f"📝 Raw AI response preview: {content[:200]}...")
            
            # Parse the JSON response
            print(f"🔄 Parsing JSON response")
            import json
            try:
                # Find JSON in the response (it might be wrapped in markdown)
                import re
                json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"🔍 DEBUG: Found JSON in markdown code block")
                else:
                    # Try to find JSON without markdown
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(0)
                        print(f"🔍 DEBUG: Found JSON without markdown")
                    else:
                        json_str = content
                        print(f"🔍 DEBUG: Using entire content as JSON")
                
                # Check if the extracted JSON contains the expected fields
                has_summary = '"summary"' in json_str
                has_is_mult = '"is_mult"' in json_str
                has_log_entries = '"log_entries"' in json_str
                print(f"🔍 DEBUG: Extracted JSON contains:")
                print(f"   - 'summary': {has_summary}")
                print(f"   - 'is_mult': {has_is_mult}")
                print(f"   - 'log_entries': {has_log_entries}")
                
                # If the extracted JSON doesn't contain the expected fields, try to extract from the full content
                if not has_summary or not has_is_mult:
                    print(f"🔍 DEBUG: Missing fields in extracted JSON, trying full content")
                    full_content_has_summary = '"summary"' in content
                    full_content_has_is_mult = '"is_mult"' in content
                    print(f"🔍 DEBUG: Full content contains:")
                    print(f"   - 'summary': {full_content_has_summary}")
                    print(f"   - 'is_mult': {full_content_has_is_mult}")
                    
                    if full_content_has_summary and not has_summary:
                        print(f"🔍 DEBUG: Summary found in full content but not in extracted JSON")
                        # Try to extract JSON from full content
                        json_match_full = re.search(r'\{.*\}', content, re.DOTALL)
                        if json_match_full:
                            json_str = json_match_full.group(0)
                            print(f"🔍 DEBUG: Re-extracted JSON from full content")
                            print(f"🔍 DEBUG: New JSON length: {len(json_str)}")
                            print(f"🔍 DEBUG: New JSON preview: {json_str[:500]}...")
                
                print(f"🔍 DEBUG: Extracted JSON string length: {len(json_str)}")
                print(f"🔍 DEBUG: Extracted JSON preview: {json_str[:500]}...")
                
                # If JSON is truncated, try to find a complete JSON structure
                if not has_summary or not has_is_mult:
                    print(f"🔍 DEBUG: JSON appears to be truncated, looking for complete structure")
                    # Try to find the last complete JSON object
                    brace_count = 0
                    start_pos = json_str.find('{')
                    if start_pos != -1:
                        for i, char in enumerate(json_str[start_pos:], start_pos):
                            if char == '{':
                                brace_count += 1
                            elif char == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    # Found complete JSON object
                                    complete_json = json_str[start_pos:i+1]
                                    print(f"🔍 DEBUG: Found complete JSON object ending at position {i}")
                                    print(f"🔍 DEBUG: Complete JSON length: {len(complete_json)}")
                                    print(f"🔍 DEBUG: Complete JSON preview: {complete_json[:500]}...")
                                    
                                    # Check if complete JSON has the fields
                                    complete_has_summary = '"summary"' in complete_json
                                    complete_has_is_mult = '"is_mult"' in complete_json
                                    print(f"🔍 DEBUG: Complete JSON contains:")
                                    print(f"   - 'summary': {complete_has_summary}")
                                    print(f"   - 'is_mult': {complete_has_is_mult}")
                                    
                                    if complete_has_summary and complete_has_is_mult:
                                        json_str = complete_json
                                        print(f"🔍 DEBUG: Using complete JSON object")
                                        break
                
                # Check JSON before fixing
                before_fix_has_summary = '"summary"' in json_str
                before_fix_has_is_mult = '"is_mult"' in json_str
                print(f"🔍 DEBUG: Before fix - has_summary: {before_fix_has_summary}, has_is_mult: {before_fix_has_is_mult}")
                
                # Try to fix common JSON issues
                json_str = self.fix_json_string(json_str)
                
                # Check JSON after fixing
                after_fix_has_summary = '"summary"' in json_str
                after_fix_has_is_mult = '"is_mult"' in json_str
                print(f"🔍 DEBUG: After fix - has_summary: {after_fix_has_summary}, has_is_mult: {after_fix_has_is_mult}")
                
                if before_fix_has_summary and not after_fix_has_summary:
                    print(f"❌ WARNING: Summary field was lost during JSON fixing!")
                if before_fix_has_is_mult and not after_fix_has_is_mult:
                    print(f"❌ WARNING: Is_mult field was lost during JSON fixing!")
                
                structured_data = json.loads(json_str)
                print(f"✅ JSON parsed successfully")
                print(f"📝 Structured data keys: {list(structured_data.keys())}")
                print(f"🔍 DEBUG: Raw structured data: {structured_data}")
                
                # Check structured data before cleaning
                before_clean_has_summary = 'summary' in structured_data
                before_clean_has_is_mult = 'is_mult' in structured_data
                print(f"🔍 DEBUG: Before cleaning - has_summary: {before_clean_has_summary}, has_is_mult: {before_clean_has_is_mult}")
                if before_clean_has_summary:
                    print(f"🔍 DEBUG: Raw summary value: {structured_data.get('summary')}")
                if before_clean_has_is_mult:
                    print(f"🔍 DEBUG: Raw is_mult value: {structured_data.get('is_mult')}")
                
                # Validate and clean the data
                print(f"🔄 Validating and cleaning structured data")
                cleaned_data = self.validate_and_clean_data(structured_data)
                print(f"✅ Data validation and cleaning completed")
                print(f"🔍 DEBUG: Final cleaned data keys: {list(cleaned_data.keys())}")
                print(f"🔍 DEBUG: Final summary: {cleaned_data.get('summary')}")
                print(f"🔍 DEBUG: Final is_mult: {cleaned_data.get('is_mult')}")
                
                if before_clean_has_summary and not cleaned_data.get('summary'):
                    print(f"❌ WARNING: Summary field was lost during cleaning!")
                if before_clean_has_is_mult and cleaned_data.get('is_mult') is None:
                    print(f"❌ WARNING: Is_mult field was lost during cleaning!")
                
                return cleaned_data
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing error: {e}")
                print(f"📝 Content that failed to parse: {content[:500]}...")
                print(f"📝 JSON string length: {len(json_str) if 'json_str' in locals() else 'N/A'}")
                
                # Try to fix the JSON and parse again
                try:
                    print(f"🔄 Attempting to fix JSON and retry parsing")
                    fixed_json = self.fix_json_string(json_str if 'json_str' in locals() else content)
                    structured_data = json.loads(fixed_json)
                    print(f"✅ JSON fixed and parsed successfully")
                    
                    # Validate and clean the data
                    cleaned_data = self.validate_and_clean_data(structured_data)
                    return cleaned_data
                    
                except Exception as retry_error:
                    print(f"❌ JSON fix attempt also failed: {retry_error}")
                    
                    # Try to extract partial data from the truncated JSON
                    try:
                        print(f"🔄 Attempting to extract partial data from truncated JSON")
                        partial_data = self.extract_partial_json(json_str if 'json_str' in locals() else content)
                        if partial_data:
                            print(f"✅ Partial data extracted successfully")
                            cleaned_data = self.validate_and_clean_data(partial_data)
                            return cleaned_data
                    except Exception as partial_error:
                        print(f"❌ Partial extraction also failed: {partial_error}")
                    
                    raise ValueError(f"Failed to parse AI response as JSON: {e}")
                
        except Exception as e:
            print(f"❌ ERROR in analyze_maintenance_log: {e}")
            import traceback
            print(f"❌ ERROR traceback: {traceback.format_exc()}")
            raise e

    def fix_json_string(self, json_str):
        """Fix common JSON issues"""
        print(f"🔍 DEBUG: Starting JSON fix process")
        print(f"🔍 DEBUG: Original JSON length: {len(json_str)}")
        print(f"🔍 DEBUG: Original JSON preview: {json_str[:300]}...")
        
        if not json_str:
            return "{}"
        
        # Remove any trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix unclosed brackets/braces by adding missing ones
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        open_brackets = json_str.count('[')
        close_brackets = json_str.count(']')
        
        # Add missing closing braces
        while close_braces < open_braces:
            json_str += '}'
            close_braces += 1
        
        # Add missing closing brackets
        while close_brackets < open_brackets:
            json_str += ']'
            close_brackets += 1
        
        # Fix unclosed quotes
        quote_count = json_str.count('"')
        if quote_count % 2 != 0:
            # Find the last unclosed quote and add a closing quote
            last_quote_pos = json_str.rfind('"')
            if last_quote_pos != -1:
                # Look for the next character after the quote
                next_char_pos = last_quote_pos + 1
                if next_char_pos < len(json_str):
                    next_char = json_str[next_char_pos]
                    if next_char not in [',', '}', ']', '\n', '\r', '\t']:
                        # Insert a quote after the last quote
                        json_str = json_str[:next_char_pos] + '"' + json_str[next_char_pos:]
        
        print(f"🔍 DEBUG: Fixed JSON length: {len(json_str)}")
        print(f"🔍 DEBUG: Fixed JSON preview: {json_str[:300]}...")
        return json_str

    def validate_and_clean_data(self, data):
        """Validate and clean the structured data from AI"""
        print(f"🔄 Validating and cleaning data")
        
        # Check if this is the new format with log_entries
        if 'log_entries' in data and isinstance(data.get('log_entries'), list):
            print(f"✅ Detected new format with log_entries array")
            return self.validate_new_format(data)
        else:
            print(f"⚠️ Detected old single-entry format, converting to new format")
            return self.convert_old_to_new_format(data)
    
    def validate_new_format(self, data):
        """Validate and clean data in the new format with log_entries array"""
        print(f"🔍 DEBUG: Raw AI response data keys: {list(data.keys())}")
        print(f"🔍 DEBUG: Summary field in raw data: {data.get('summary')}")
        print(f"🔍 DEBUG: Is_mult field in raw data: {data.get('is_mult')}")
        
        cleaned_data = {
            'aircraft_registration': self.clean_string(data.get('aircraft_registration')),
            'aircraft_make_model': self.clean_string(data.get('aircraft_make_model')),
            'summary': self.clean_string(data.get('summary')),
            'is_mult': self.clean_boolean(data.get('is_mult', False)),
            'log_entries': []
        }
        
        print(f"🔍 DEBUG: Cleaned summary: {cleaned_data['summary']}")
        print(f"🔍 DEBUG: Cleaned is_mult: {cleaned_data['is_mult']}")
        
        # Clean each log entry
        for entry in data.get('log_entries', []):
            cleaned_entry = self.clean_log_entry(entry)
            cleaned_data['log_entries'].append(cleaned_entry)
        
        print(f"✅ New format validation completed with {len(cleaned_data['log_entries'])} entries")
        return cleaned_data
    
    def convert_old_to_new_format(self, data):
        """Convert old single-entry format to new format with log_entries array"""
        print(f"🔍 DEBUG: Converting old format data keys: {list(data.keys())}")
        print(f"🔍 DEBUG: Summary field in old data: {data.get('summary')}")
        
        # Extract aircraft info from the old structure
        aircraft_registration = self.clean_string(data.get('aircraft_registration'))
        aircraft_make_model = self.clean_string(data.get('aircraft_make_model'))
        
        # Create a single log entry from the old data
        log_entry = self.clean_log_entry(data)
        
        # Create new format with default values for new fields
        cleaned_data = {
            'aircraft_registration': aircraft_registration,
            'aircraft_make_model': aircraft_make_model,
            'summary': self.clean_string(data.get('summary')),
            'is_mult': False,  # Old format is always single entry
            'log_entries': [log_entry]
        }
        
        print(f"🔍 DEBUG: Converted summary: {cleaned_data['summary']}")
        print(f"🔍 DEBUG: Converted is_mult: {cleaned_data['is_mult']}")
        print(f"✅ Converted old format to new format")
        return cleaned_data
    
    def clean_log_entry(self, entry):
        """Clean a single log entry"""
        cleaned_entry = {
            'description_of_work_performed': self.clean_string(entry.get('description_of_work_performed')),
            'tach_time': self.clean_string(entry.get('tach_time')),
            'hobbs_time': self.clean_string(entry.get('hobbs_time')),
            'part_number_replaced': self.clean_part_numbers(entry.get('part_number_replaced')),
            'manual_reference': self.clean_string(entry.get('manual_reference')),
            'reason_for_maintenance': self.clean_string(entry.get('reason_for_maintenance')),
            'ad_compliance': self.clean_string(entry.get('ad_compliance')),
            'next_due_compliance': self.clean_string(entry.get('next_due_compliance')),
            'service_bulletin_reference': self.clean_string(entry.get('service_bulletin_reference')),
            'certification_statement': self.clean_string(entry.get('certification_statement')),
            'performed_by': self.clean_string(entry.get('performed_by')),
            'license_number': self.clean_string(entry.get('license_number')),
            'date': self.clean_string(entry.get('date')),
            'risk_level': self.clean_string(entry.get('risk_level')),
            'urgency': self.clean_string(entry.get('urgency')),
            'is_airworthy': self.clean_boolean(entry.get('is_airworthy'))
        }
        return cleaned_entry
    
    def clean_string(self, value):
        """Clean a string value"""
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if value.lower() in ['unknown', 'n/a', 'none', '']:
                print(f"🔍 DEBUG: String cleaned to None: '{value}'")
                return None
        cleaned = str(value) if value is not None else None
        if value != cleaned:
            print(f"🔍 DEBUG: String cleaned: '{value}' -> '{cleaned}'")
        return cleaned
    
    def clean_part_numbers(self, value):
        """Clean part numbers array"""
        if value is None:
            return []
        if isinstance(value, str):
            return [value.strip()] if value.strip() else []
        if isinstance(value, list):
            return [str(item).strip() for item in value if item and str(item).strip()]
        return []
    
    def clean_boolean(self, value):
        """Clean boolean value"""
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            result = value.lower() in ['true', 'yes', 'airworthy', '1']
            print(f"🔍 DEBUG: Boolean cleaned: '{value}' -> {result}")
            return result
        print(f"🔍 DEBUG: Boolean default value: {value} -> True")
        return True  # Default to True for airworthiness

    def validate_aircraft_registration(self, registration):
        """Validate aircraft registration format"""
        if not registration:
            return False
        
        # Basic validation for common formats
        registration = registration.upper().strip()
        
        # US format: N followed by 1-5 alphanumeric characters
        if registration.startswith('N') and len(registration) <= 6:
            return True
        
        # International format: 2-3 letters followed by 1-4 alphanumeric characters
        import re
        if re.match(r'^[A-Z]{2,3}[A-Z0-9]{1,4}$', registration):
            return True
        
        return False

    def assess_risk_level(self, data):
        """Assess risk level based on maintenance data"""
        risk_factors = []
        
        # Check for critical maintenance items
        critical_keywords = ['engine', 'propeller', 'landing gear', 'flight control', 'fuel system']
        work_description = data.get('description_of_work_performed', '').lower()
        
        for keyword in critical_keywords:
            if keyword in work_description:
                risk_factors.append(f"Critical {keyword} maintenance")
        
        # Check for AD compliance issues
        ad_compliance = data.get('ad_compliance', '').lower()
        if 'non-compliant' in ad_compliance or 'overdue' in ad_compliance:
            risk_factors.append("AD compliance issues")
        
        # Determine risk level
        if len(risk_factors) >= 2:
            return "High"
        elif len(risk_factors) == 1:
            return "Medium"
        else:
            return "Low"

    def determine_urgency(self, data):
        """Determine urgency based on maintenance data"""
        urgency_factors = []
        
        # Check for time-sensitive items
        time_keywords = ['overdue', 'expired', 'due', 'required']
        work_description = data.get('description_of_work_performed', '').lower()
        
        for keyword in time_keywords:
            if keyword in work_description:
                urgency_factors.append(f"Time-sensitive: {keyword}")
        
        # Check for safety-related items
        safety_keywords = ['safety', 'critical', 'emergency', 'grounded']
        for keyword in safety_keywords:
            if keyword in work_description:
                urgency_factors.append(f"Safety-related: {keyword}")
        
        # Determine urgency
        if len(urgency_factors) >= 2:
            return "High"
        elif len(urgency_factors) == 1:
            return "Medium"
        else:
            return "Normal" 

    def extract_partial_json(self, json_str):
        """Extract partial data from truncated JSON"""
        try:
            print(f"🔍 DEBUG: Starting partial JSON extraction")
            print(f"🔍 DEBUG: JSON string length: {len(json_str)}")
            print(f"🔍 DEBUG: JSON string preview: {json_str[:500]}...")
            
            # Check if summary and is_mult are present in the raw string
            summary_in_string = '"summary"' in json_str
            is_mult_in_string = '"is_mult"' in json_str
            print(f"🔍 DEBUG: 'summary' found in string: {summary_in_string}")
            print(f"🔍 DEBUG: 'is_mult' found in string: {is_mult_in_string}")
            
            # Find the position of summary and is_mult in the string
            summary_pos = json_str.find('"summary"')
            is_mult_pos = json_str.find('"is_mult"')
            print(f"🔍 DEBUG: 'summary' position: {summary_pos}")
            print(f"🔍 DEBUG: 'is_mult' position: {is_mult_pos}")
            
            if summary_pos != -1:
                print(f"🔍 DEBUG: Context around 'summary': {json_str[max(0, summary_pos-50):summary_pos+100]}")
            if is_mult_pos != -1:
                print(f"🔍 DEBUG: Context around 'is_mult': {json_str[max(0, is_mult_pos-50):is_mult_pos+50]}")
            
            # Try to find the start of the JSON structure
            start_pos = json_str.find('{')
            if start_pos == -1:
                print(f"❌ No opening brace found in JSON string")
                return None
            
            # Find the aircraft registration and make/model
            aircraft_reg_match = re.search(r'"aircraft_registration"\s*:\s*"([^"]*)"', json_str)
            aircraft_model_match = re.search(r'"aircraft_make_model"\s*:\s*"([^"]*)"', json_str)
            
            # Find summary and is_mult fields - use a more robust approach
            # Try multiple patterns for summary to handle different JSON formats
            summary_match = None
            summary_patterns = [
                r'"summary"\s*:\s*"([^"]*)"',  # Basic pattern
                r'"summary"\s*:\s*"([^"]*)"',  # With DOTALL flag
                r'"summary"\s*:\s*"((?:[^"\\]|\\.)*)"',  # Robust pattern
            ]
            
            for pattern in summary_patterns:
                summary_match = re.search(pattern, json_str, re.DOTALL)
                if summary_match:
                    print(f"🔍 DEBUG: Summary found with pattern: {pattern}")
                    break
            
            is_mult_match = re.search(r'"is_mult"\s*:\s*(true|false)', json_str)
            
            aircraft_registration = aircraft_reg_match.group(1) if aircraft_reg_match else "Unknown"
            aircraft_make_model = aircraft_model_match.group(1) if aircraft_model_match else "Unknown"
            summary = summary_match.group(1) if summary_match else None
            is_mult = is_mult_match.group(1).lower() == "true" if is_mult_match else False
            
            # Fallback: If regex failed, try to extract manually
            if summary is None and summary_pos != -1:
                print(f"🔍 DEBUG: Trying manual summary extraction")
                # Find the start of the summary value
                summary_start = json_str.find('"summary"', summary_pos)
                if summary_start != -1:
                    # Find the colon after "summary"
                    colon_pos = json_str.find(':', summary_start)
                    if colon_pos != -1:
                        # Find the opening quote
                        quote_start = json_str.find('"', colon_pos)
                        if quote_start != -1:
                            # Find the closing quote
                            quote_end = json_str.find('"', quote_start + 1)
                            if quote_end != -1:
                                summary = json_str[quote_start + 1:quote_end]
                                print(f"🔍 DEBUG: Manually extracted summary: {summary}")
            
            if not is_mult_match and is_mult_pos != -1:
                print(f"🔍 DEBUG: Trying manual is_mult extraction")
                # Find the start of the is_mult value
                is_mult_start = json_str.find('"is_mult"', is_mult_pos)
                if is_mult_start != -1:
                    # Find the colon after "is_mult"
                    colon_pos = json_str.find(':', is_mult_start)
                    if colon_pos != -1:
                        # Find the value (true or false)
                        value_start = colon_pos + 1
                        while value_start < len(json_str) and json_str[value_start].isspace():
                            value_start += 1
                        if value_start < len(json_str):
                            if json_str.startswith('true', value_start):
                                is_mult = True
                                print(f"🔍 DEBUG: Manually extracted is_mult: true")
                            elif json_str.startswith('false', value_start):
                                is_mult = False
                                print(f"🔍 DEBUG: Manually extracted is_mult: false")
            
            print(f"🔍 DEBUG: Regex match results:")
            print(f"   - Aircraft registration match: {aircraft_reg_match is not None}")
            print(f"   - Aircraft make/model match: {aircraft_model_match is not None}")
            print(f"   - Summary match: {summary_match is not None}")
            print(f"   - Is_mult match: {is_mult_match is not None}")
            print(f"   - Extracted summary: {summary}")
            print(f"   - Extracted is_mult: {is_mult}")
            
            # Try to extract log entries
            log_entries = []
            
            # Find all log entry objects
            entry_pattern = r'\{[^{}]*"description_of_work_performed"[^{}]*\}'
            entry_matches = re.findall(entry_pattern, json_str, re.DOTALL)
            
            for entry_str in entry_matches:
                try:
                    # Try to parse each entry
                    entry_data = json.loads(entry_str)
                    log_entries.append(entry_data)
                except:
                    # If individual entry fails, try to extract key fields manually
                    entry_data = self.extract_entry_fields(entry_str)
                    if entry_data:
                        log_entries.append(entry_data)
            
            if log_entries:
                result = {
                    "aircraft_registration": aircraft_registration,
                    "aircraft_make_model": aircraft_make_model,
                    "summary": summary,
                    "is_mult": is_mult,
                    "log_entries": log_entries
                }
                print(f"🔍 DEBUG: Partial JSON extraction result:")
                print(f"   - Aircraft registration: {aircraft_registration}")
                print(f"   - Aircraft make/model: {aircraft_make_model}")
                print(f"   - Summary: {summary}")
                print(f"   - Is mult: {is_mult}")
                print(f"   - Number of log entries: {len(log_entries)}")
                return result
            
            return None
            
        except Exception as e:
            print(f"❌ Error extracting partial JSON: {e}")
            return None
    
    def extract_entry_fields(self, entry_str):
        """Extract individual fields from a log entry string"""
        try:
            entry_data = {}
            
            # Extract common fields using regex
            fields = [
                ("description_of_work_performed", r'"description_of_work_performed"\s*:\s*"([^"]*)"'),
                ("tach_time", r'"tach_time"\s*:\s*"([^"]*)"'),
                ("hobbs_time", r'"hobbs_time"\s*:\s*"([^"]*)"'),
                ("manual_reference", r'"manual_reference"\s*:\s*"([^"]*)"'),
                ("reason_for_maintenance", r'"reason_for_maintenance"\s*:\s*"([^"]*)"'),
                ("ad_compliance", r'"ad_compliance"\s*:\s*"([^"]*)"'),
                ("next_due_compliance", r'"next_due_compliance"\s*:\s*"([^"]*)"'),
                ("service_bulletin_reference", r'"service_bulletin_reference"\s*:\s*"([^"]*)"'),
                ("certification_statement", r'"certification_statement"\s*:\s*"([^"]*)"'),
                ("performed_by", r'"performed_by"\s*:\s*"([^"]*)"'),
                ("license_number", r'"license_number"\s*:\s*"([^"]*)"'),
                ("date", r'"date"\s*:\s*"([^"]*)"'),
                ("risk_level", r'"risk_level"\s*:\s*"([^"]*)"'),
                ("urgency", r'"urgency"\s*:\s*"([^"]*)"'),
            ]
            
            for field_name, pattern in fields:
                match = re.search(pattern, entry_str)
                if match:
                    entry_data[field_name] = match.group(1)
                else:
                    entry_data[field_name] = None
            
            # Handle part_number_replaced as array
            part_numbers_match = re.search(r'"part_number_replaced"\s*:\s*\[([^\]]*)\]', entry_str)
            if part_numbers_match:
                part_numbers_str = part_numbers_match.group(1)
                # Extract individual part numbers
                part_numbers = re.findall(r'"([^"]*)"', part_numbers_str)
                entry_data["part_number_replaced"] = part_numbers
            else:
                entry_data["part_number_replaced"] = []
            
            # Handle is_airworthy as boolean
            airworthy_match = re.search(r'"is_airworthy"\s*:\s*(true|false)', entry_str)
            if airworthy_match:
                entry_data["is_airworthy"] = airworthy_match.group(1).lower() == "true"
            else:
                entry_data["is_airworthy"] = True
            
            return entry_data
            
        except Exception as e:
            print(f"❌ Error extracting entry fields: {e}")
            return None 