#!/usr/bin/env python3
"""
Test script to debug JSON parsing issues with summary field
"""

import re
import json
import os
import sys

# Add the current directory to the path so we can import ai_service
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_service import AIService

def test_json_parsing():
    """Test the JSON parsing methods"""
    
    # Sample JSON that might be causing issues
    test_json = '''
    {
      "aircraft_registration": "N123AB",
      "aircraft_make_model": "Cessna 172",
      "summary": "Multiple maintenance entries including tire replacement and engine inspection",
      "is_mult": true,
      "log_entries": [
        {
          "description_of_work_performed": "Replaced left main landing gear tire",
          "tach_time": "1250.5",
          "hobbs_time": "1250.5",
          "part_number_replaced": ["Tire-123", "Tube-456"],
          "manual_reference": "Aircraft Maintenance Manual Chapter 32",
          "reason_for_maintenance": "Scheduled maintenance",
          "ad_compliance": "AD 2023-15-02 complied with",
          "next_due_compliance": "Next inspection due in 50 hours",
          "service_bulletin_reference": "SB 2023-01",
          "certification_statement": "I certify that this aircraft is airworthy",
          "performed_by": "John Smith",
          "license_number": "A&P 123456",
          "date": "2024-01-15",
          "risk_level": "Low",
          "urgency": "Normal",
          "is_airworthy": true
        }
      ]
    }
    '''
    
    # Test the regex patterns
    print("=== Testing Regex Patterns ===")
    
    # Test summary extraction
    summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', test_json, re.DOTALL)
    print(f"Summary match: {summary_match is not None}")
    if summary_match:
        print(f"Extracted summary: {summary_match.group(1)}")
    
    # Test is_mult extraction
    is_mult_match = re.search(r'"is_mult"\s*:\s*(true|false)', test_json)
    print(f"Is_mult match: {is_mult_match is not None}")
    if is_mult_match:
        print(f"Extracted is_mult: {is_mult_match.group(1)}")
    
    # Test aircraft registration extraction
    aircraft_reg_match = re.search(r'"aircraft_registration"\s*:\s*"([^"]*)"', test_json)
    print(f"Aircraft registration match: {aircraft_reg_match is not None}")
    if aircraft_reg_match:
        print(f"Extracted aircraft registration: {aircraft_reg_match.group(1)}")
    
    # Test aircraft make/model extraction
    aircraft_model_match = re.search(r'"aircraft_make_model"\s*:\s*"([^"]*)"', test_json)
    print(f"Aircraft make/model match: {aircraft_model_match is not None}")
    if aircraft_model_match:
        print(f"Extracted aircraft make/model: {aircraft_model_match.group(1)}")
    
    print("\n=== Testing AI Service Methods ===")
    
    # Create AI service instance (without API key for testing)
    try:
        ai_service = AIService()
    except ValueError as e:
        print(f"Warning: Could not initialize AI service with API key: {e}")
        print("Creating mock AI service for testing...")
        # Create a mock class for testing
        class MockAIService:
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
            
            def extract_partial_json(self, json_str):
                """Extract partial data from truncated JSON"""
                try:
                    print(f"🔍 DEBUG: Starting partial JSON extraction")
                    print(f"🔍 DEBUG: JSON string length: {len(json_str)}")
                    print(f"🔍 DEBUG: JSON string preview: {json_str[:500]}...")
                    
                    # Try to find the start of the JSON structure
                    start_pos = json_str.find('{')
                    if start_pos == -1:
                        print(f"❌ No opening brace found in JSON string")
                        return None
                    
                    # Find the aircraft registration and make/model
                    aircraft_reg_match = re.search(r'"aircraft_registration"\s*:\s*"([^"]*)"', json_str)
                    aircraft_model_match = re.search(r'"aircraft_make_model"\s*:\s*"([^"]*)"', json_str)
                    
                    # Find summary and is_mult fields - use a more robust approach
                    summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', json_str, re.DOTALL)
                    is_mult_match = re.search(r'"is_mult"\s*:\s*(true|false)', json_str)
                    
                    aircraft_registration = aircraft_reg_match.group(1) if aircraft_reg_match else "Unknown"
                    aircraft_make_model = aircraft_model_match.group(1) if aircraft_model_match else "Unknown"
                    summary = summary_match.group(1) if summary_match else None
                    is_mult = is_mult_match.group(1).lower() == "true" if is_mult_match else False
                    
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
                    is_airworthy_match = re.search(r'"is_airworthy"\s*:\s*(true|false)', entry_str)
                    if is_airworthy_match:
                        entry_data["is_airworthy"] = is_airworthy_match.group(1).lower() == "true"
                    else:
                        entry_data["is_airworthy"] = True
                    
                    return entry_data
                    
                except Exception as e:
                    print(f"❌ Error extracting entry fields: {e}")
                    return None
            
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
                
                return cleaned_data
            
            def clean_log_entry(self, entry):
                """Clean a single log entry"""
                if not isinstance(entry, dict):
                    return {}
                
                return {
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
                    'is_airworthy': self.clean_boolean(entry.get('is_airworthy', True))
                }
            
            def clean_string(self, value):
                """Clean string values"""
                if value is None:
                    return None
                return str(value).strip()
            
            def clean_part_numbers(self, value):
                """Clean part numbers array"""
                if value is None:
                    return []
                if isinstance(value, list):
                    return [str(item).strip() for item in value if item]
                return [str(value).strip()]
            
            def clean_boolean(self, value):
                """Clean boolean values"""
                if value is None:
                    return False
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ['true', '1', 'yes', 'on']
        
        ai_service = MockAIService()
    
    # Test fix_json_string
    print("Testing fix_json_string...")
    fixed_json = ai_service.fix_json_string(test_json)
    print(f"Fixed JSON length: {len(fixed_json)}")
    
    # Test extract_partial_json
    print("Testing extract_partial_json...")
    partial_data = ai_service.extract_partial_json(test_json)
    if partial_data:
        print(f"Extracted data keys: {list(partial_data.keys())}")
        print(f"Summary: {partial_data.get('summary')}")
        print(f"Is_mult: {partial_data.get('is_mult')}")
        print(f"Number of log entries: {len(partial_data.get('log_entries', []))}")
    else:
        print("No partial data extracted")
    
    # Test validate_and_clean_data
    print("Testing validate_and_clean_data...")
    try:
        parsed_json = json.loads(test_json)
        cleaned_data = ai_service.validate_and_clean_data(parsed_json)
        print(f"Cleaned data keys: {list(cleaned_data.keys())}")
        print(f"Final summary: {cleaned_data.get('summary')}")
        print(f"Final is_mult: {cleaned_data.get('is_mult')}")
    except Exception as e:
        print(f"Error in validate_and_clean_data: {e}")

if __name__ == "__main__":
    test_json_parsing() 