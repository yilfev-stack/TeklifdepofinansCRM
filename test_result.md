#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus: "What is being tested now"
##   stuck_tasks: ["List of tasks that are stuck"]
##   test_all: false
##   test_priority: ["high", "medium", "low"]

# IMPORTANT RULES:
# 1. Main agent must update test_result.md before calling testing agent
# 2. Testing agent must update test_result.md after completing tests
# 3. Status is determined by testing agent's observations, not assumptions
# 4. On user feedback, update status_history to contain the user concern and problem

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  Real Costs Module - Gerçek Maliyetler Modülü
  - Çift Defter Sistemi: Nakit (Banka) + Kredi Kartı Borcu
  - Banka ve Kredi Kartı ekstrelerini ayrı yükleme
  - Açılış bakiyesi ayarlama (nakit + kart borcu)
  - Mükerrer kontrolü: Dekont No + Tutar kombinasyonu
  - Aylık döküm ve detaylı işlem görüntüleme
  - Hedef: Excel'deki son bakiye ile sistem bakiyesinin eşleşmesi

backend:
  - task: "Warehouse CRUD (Create, Read, Update, Delete)"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Tested via curl - create, list, delete working. Soft delete supported."

  - task: "Rack Group CRUD"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Tested via curl - create, list with warehouse_id filter working."

  - task: "Rack Level CRUD"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Tested via curl - create, list with rack_group_id filter working."

  - task: "Rack Slot CRUD"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Tested via curl - create, list with rack_level_id filter working."

  - task: "Stock In (Stok Girişi)"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Tested - adds stock to location, creates movement log, builds full address."

  - task: "Stock Transfer"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Tested - transfers 3 units from Pendik to Maltepe. Source decreased, target increased, movement logged."

  - task: "Stock Movements Log"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "All movements logged with type, quantity, source/target addresses."

  - task: "Reports - By Warehouse"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Returns warehouse summary with total items, quantity, reserved."

  - task: "Reports - By Product"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Returns product/variant summary with locations count, total qty."

  - task: "Inventory Count"
    implemented: true
    working: "NA"
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Backend implemented, frontend UI not yet completed. Needs testing."

  - task: "Low Stock Alert"
    implemented: true
    working: true
    file: "/app/backend/warehouse_routes.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "API endpoint working. Returns items below min_stock level."

frontend:
  - task: "Warehouse Page - Tabs Navigation"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "4 tabs working: Depolar, Stok, Hareketler, Raporlar"

  - task: "Warehouse Management UI"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Create, edit, delete warehouse. Cards with edit/delete buttons visible."

  - task: "Hierarchy Navigation (Depo > Raf > Kat > Bölme)"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Breadcrumb navigation working. Click warehouse > rack group > level shows slots."

  - task: "Stock In Dialog"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Full dialog with product, variant, location (4-level), quantity, reference, note fields."

  - task: "Transfer Dialog"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Full dialog with source address (orange), target address (green), product, variant, quantity."

  - task: "Stock List View"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Shows full address, product/model, quantity, reserved, available."

  - task: "Movements Log View"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Shows date, type (IN/OUT/TRANSFER badge), product, source/target address, quantity, note."

  - task: "Reports View"
    implemented: true
    working: true
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: true
        agent: "main"
        comment: "Depo bazlı ve ürün bazlı raporlar çalışıyor."

  - task: "Inventory Count UI"
    implemented: false
    working: "NA"
    file: "/app/frontend/src/pages/Warehouse.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Backend ready. Frontend UI for inventory count not yet implemented."

metadata:
  created_by: "main_agent"
  version: "1.0"
  test_sequence: 1
  run_ui: true

test_plan:
  current_focus: "Real Costs Module - Backend & Frontend Testing"
  stuck_tasks: []
  test_all: false
  test_priority: ["high"]

incorporate_user_feedback: |
  - CRITICAL: Bank statement balance MUST match Excel final balance (37,298.38 TL)
  - Duplicate control must use Dekont No + Amount combination (not just Dekont No)
  - Bank fee transactions have same Dekont No as main transfer - both must be included
  - Negative card debt should show as "Kart Alacağı" (overpayment to card)

real_costs_tests:
  - task: "Bank Statement Upload"
    endpoint: "POST /api/real-costs/upload"
    test_file: "/app/backend/hesaphareketleri.xls"
    source_type: "bank"
    expected_records: 303
    expected_skipped: 0
    priority: "high"
    status: "PASSED"
    
  - task: "Opening Balance Setup"
    endpoint: "POST /api/real-costs/opening-balances"
    test_data: '{"opening_cash": 27670.20, "opening_card_debt": 0}'
    priority: "high"
    status: "PASSED"
    
  - task: "Summary Calculation"
    endpoint: "GET /api/real-costs/summary"
    expected_cash: 37298.38
    priority: "high"
    status: "PASSED"
    
  - task: "Credit Card Statement Upload"
    endpoint: "POST /api/real-costs/upload"
    test_file: "/app/backend/kredi_karti_ekstresi.xls"
    source_type: "card"
    expected_records: 33
    priority: "high"
    status: "PASSED"
    
  - task: "Frontend KPI Display"
    page: "/real-costs"
    password: "984027"
    expected_kpis: ["Mevcut Nakit", "Kart Alacağı/Borcu", "Net Durum"]
    priority: "high"
    status: "PASSED"
