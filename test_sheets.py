#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test Google Sheets Connection
"""
from google.oauth2 import service_account
from googleapiclient.discovery import build

CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = '1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def test_connection():
    try:
        print("🔌 Đang kiểm tra kết nối...")
        
        # Load credentials
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES)
        print("✅ Đã tải credentials thành công")
        
        # Build service
        service = build('sheets', 'v4', credentials=credentials)
        print("✅ Đã khởi tạo Google Sheets API")
        
        # Test get spreadsheet
        result = service.spreadsheets().get(
            spreadsheetId=SPREADSHEET_ID
        ).execute()
        
        print(f"\n✅ KẾT NỐI THÀNH CÔNG!")
        print(f"📊 Sheet Title: {result['properties']['title']}")
        
        # List all sheets
        sheets = result.get('sheets', [])
        print(f"\n📋 Danh sách sheets ({len(sheets)}):")
        for sheet in sheets:
            print(f"  - {sheet['properties']['title']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ LỖI KẾT NỐI: {str(e)}")
        print("\n⚠️ Các bước kiểm tra:")
        print("1. Kiểm tra file credentials.json có tồn tại")
        print("2. Kiểm tra service account email đã được share quyền vào Google Sheet")
        print("3. Service account email: sheets-updater-service@marketstack-sheets-480804.iam.gserviceaccount.com")
        print("4. Google Sheet URL: https://docs.google.com/spreadsheets/d/1TKmu6oRIEqyG2PfY__deAhp_8em9pkD7PdUUU9DqhfA/edit")
        return False

if __name__ == '__main__':
    test_connection()
