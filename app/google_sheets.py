"""
Google Sheets Integration Module for Pathvancer Chatbot

Provides functionality to:
- Read knowledge base from Google Sheets
- Log chat responses to Google Sheets
- Store session data in Google Sheets
"""

import gspread
from google.oauth2.service_account import Credentials
from typing import List, Dict, Any, Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# Google Sheets scopes
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


class GoogleSheetsConnector:
    """Connect to Google Sheets using service account credentials"""
    
    def __init__(self, service_account_json_path: str):
        """
        Initialize Google Sheets connector
        
        Args:
            service_account_json_path: Path to Google service account JSON file
        """
        try:
            self.credentials = Credentials.from_service_account_file(
                service_account_json_path,
                scopes=SCOPES
            )
            self.client = gspread.authorize(self.credentials)
            logger.info("✓ Google Sheets connected successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Google Sheets: {str(e)}")
            self.client = None
    
    def open_spreadsheet(self, spreadsheet_name_or_id: str) -> Optional[Any]:
        """
        Open a Google Spreadsheet by name or ID
        
        Args:
            spreadsheet_name_or_id: Spreadsheet name or ID
            
        Returns:
            Spreadsheet object or None if failed
        """
        try:
            if self.client is None:
                return None
            
            # Try to open by ID first, then by name
            try:
                spreadsheet = self.client.open_by_key(spreadsheet_name_or_id)
                logger.info(f"✓ Opened spreadsheet by ID: {spreadsheet_name_or_id}")
            except:
                spreadsheet = self.client.open(spreadsheet_name_or_id)
                logger.info(f"✓ Opened spreadsheet by name: {spreadsheet_name_or_id}")
            
            return spreadsheet
        except Exception as e:
            logger.error(f"❌ Failed to open spreadsheet: {str(e)}")
            return None
    
    def get_worksheet(self, spreadsheet: Any, sheet_name: str) -> Optional[Any]:
        """
        Get a specific worksheet from spreadsheet
        
        Args:
            spreadsheet: Spreadsheet object
            sheet_name: Name of the worksheet
            
        Returns:
            Worksheet object or None if failed
        """
        try:
            if spreadsheet is None:
                return None
            
            worksheet = spreadsheet.worksheet(sheet_name)
            logger.info(f"✓ Accessed worksheet: {sheet_name}")
            return worksheet
        except Exception as e:
            logger.error(f"❌ Failed to get worksheet {sheet_name}: {str(e)}")
            return None


class KnowledgeBaseSheets(GoogleSheetsConnector):
    """Load knowledge base from Google Sheets"""
    
    def __init__(self, service_account_json_path: str, spreadsheet_id: str, sheet_name: str = "QA Pairs"):
        """
        Initialize knowledge base from Google Sheets
        
        Args:
            service_account_json_path: Path to service account JSON
            spreadsheet_id: Google Sheets ID or name
            sheet_name: Name of worksheet containing Q&A pairs
        """
        super().__init__(service_account_json_path)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.qa_pairs = []
        self.load_qa_pairs()
    
    def load_qa_pairs(self) -> List[Dict[str, str]]:
        """
        Load Q&A pairs from Google Sheets
        
        Expected sheet format:
        | Question | Answer | Category | Tags |
        
        Returns:
            List of Q&A pair dictionaries
        """
        try:
            if self.client is None:
                logger.warning("⚠️ Google Sheets not connected, using empty KB")
                return []
            
            spreadsheet = self.open_spreadsheet(self.spreadsheet_id)
            if spreadsheet is None:
                return []
            
            worksheet = self.get_worksheet(spreadsheet, self.sheet_name)
            if worksheet is None:
                return []
            
            # Get all values
            all_values = worksheet.get_all_values()
            
            if not all_values or len(all_values) < 2:
                logger.warning("⚠️ No data in knowledge base sheet")
                return []
            
            # First row is headers
            headers = all_values[0]
            
            # Parse Q&A pairs
            qa_pairs = []
            for row in all_values[1:]:
                if len(row) >= 2 and row[0] and row[1]:  # Question and Answer required
                    qa_pair = {
                        'question': row[0],
                        'answer': row[1],
                        'category': row[2] if len(row) > 2 else '',
                        'tags': row[3] if len(row) > 3 else ''
                    }
                    qa_pairs.append(qa_pair)
            
            self.qa_pairs = qa_pairs
            logger.info(f"✓ Loaded {len(qa_pairs)} Q&A pairs from Google Sheets")
            return qa_pairs
        
        except Exception as e:
            logger.error(f"❌ Failed to load Q&A pairs: {str(e)}")
            return []
    
    def get_qa_pairs(self) -> List[Dict[str, str]]:
        """Get loaded Q&A pairs"""
        return self.qa_pairs


class ChatResponseLogger(GoogleSheetsConnector):
    """Log chat responses to Google Sheets for analytics"""
    
    def __init__(self, service_account_json_path: str, spreadsheet_id: str, sheet_name: str = "Chat Logs"):
        """
        Initialize chat response logger
        
        Args:
            service_account_json_path: Path to service account JSON
            spreadsheet_id: Google Sheets ID or name
            sheet_name: Name of worksheet for logging
        """
        super().__init__(service_account_json_path)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.setup_sheet()
    
    def setup_sheet(self) -> None:
        """Create sheet with headers if it doesn't exist"""
        try:
            if self.client is None:
                return
            
            spreadsheet = self.open_spreadsheet(self.spreadsheet_id)
            if spreadsheet is None:
                return
            
            # Try to get worksheet, create if doesn't exist
            try:
                worksheet = self.get_worksheet(spreadsheet, self.sheet_name)
            except:
                worksheet = spreadsheet.add_worksheet(title=self.sheet_name, rows="1000", cols="20")
                logger.info(f"✓ Created new worksheet: {self.sheet_name}")
            
            # Add headers if empty
            if not worksheet.get_all_values() or len(worksheet.get_all_values()) == 0:
                headers = [
                    "Timestamp",
                    "Session ID",
                    "User ID",
                    "User Message",
                    "Bot Response",
                    "Route",
                    "Confidence",
                    "Model",
                    "Tokens Used"
                ]
                worksheet.append_row(headers)
                logger.info("✓ Added headers to chat log sheet")
        
        except Exception as e:
            logger.error(f"❌ Failed to setup sheet: {str(e)}")
    
    def log_response(self, log_data: Dict[str, Any]) -> bool:
        """
        Log a chat response to Google Sheets
        
        Args:
            log_data: Dictionary with chat information
                Required: session_id, user_id, message, response, route, confidence
                Optional: timestamp, model, tokens_used
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.client is None:
                logger.warning("⚠️ Google Sheets not connected, skipping log")
                return False
            
            spreadsheet = self.open_spreadsheet(self.spreadsheet_id)
            worksheet = self.get_worksheet(spreadsheet, self.sheet_name)
            
            if worksheet is None:
                return False
            
            from datetime import datetime
            
            # Prepare row data
            row = [
                log_data.get('timestamp', datetime.now().isoformat()),
                log_data.get('session_id', ''),
                log_data.get('user_id', ''),
                log_data.get('message', ''),
                log_data.get('response', ''),
                log_data.get('route', ''),
                log_data.get('confidence', ''),
                log_data.get('model', 'openai/gpt-3.5-turbo'),
                log_data.get('tokens_used', '')
            ]
            
            worksheet.append_row(row)
            logger.debug(f"✓ Logged response to Google Sheets")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to log response: {str(e)}")
            return False


class SessionDataSheets(GoogleSheetsConnector):
    """Store session data in Google Sheets"""
    
    def __init__(self, service_account_json_path: str, spreadsheet_id: str, sheet_name: str = "Sessions"):
        """
        Initialize session data storage
        
        Args:
            service_account_json_path: Path to service account JSON
            spreadsheet_id: Google Sheets ID or name
            sheet_name: Name of worksheet for sessions
        """
        super().__init__(service_account_json_path)
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.setup_sheet()
    
    def setup_sheet(self) -> None:
        """Create sheet with headers if it doesn't exist"""
        try:
            if self.client is None:
                return
            
            spreadsheet = self.open_spreadsheet(self.spreadsheet_id)
            if spreadsheet is None:
                return
            
            try:
                worksheet = self.get_worksheet(spreadsheet, self.sheet_name)
            except:
                worksheet = spreadsheet.add_worksheet(title=self.sheet_name, rows="1000", cols="20")
            
            if not worksheet.get_all_values():
                headers = [
                    "Session ID",
                    "User ID",
                    "Created At",
                    "Last Activity",
                    "Message Count",
                    "Status"
                ]
                worksheet.append_row(headers)
                logger.info("✓ Created sessions sheet")
        
        except Exception as e:
            logger.error(f"❌ Failed to setup sessions sheet: {str(e)}")


# Global instances
_kb_sheets: Optional[KnowledgeBaseSheets] = None
_response_logger: Optional[ChatResponseLogger] = None
_session_sheets: Optional[SessionDataSheets] = None


def init_google_sheets(service_account_path: str, spreadsheet_id: str) -> bool:
    """
    Initialize all Google Sheets connectors
    
    Args:
        service_account_path: Path to service account JSON
        spreadsheet_id: Google Sheets ID
    
    Returns:
        True if successful
    """
    global _kb_sheets, _response_logger, _session_sheets
    
    try:
        _kb_sheets = KnowledgeBaseSheets(service_account_path, spreadsheet_id, "QA Pairs")
        _response_logger = ChatResponseLogger(service_account_path, spreadsheet_id, "Chat Logs")
        _session_sheets = SessionDataSheets(service_account_path, spreadsheet_id, "Sessions")
        
        logger.info("✓ All Google Sheets connectors initialized")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize Google Sheets: {str(e)}")
        return False


def get_kb_sheets() -> Optional[KnowledgeBaseSheets]:
    """Get knowledge base sheets instance"""
    return _kb_sheets


def get_response_logger() -> Optional[ChatResponseLogger]:
    """Get response logger instance"""
    return _response_logger


def get_session_sheets() -> Optional[SessionDataSheets]:
    """Get session sheets instance"""
    return _session_sheets
