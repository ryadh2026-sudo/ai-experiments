from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from rapidfuzz import fuzz

app = FastAPI()

# السماح للواجهة الأمامية (موقع الويب) بالتحدث مع الباك إند
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # في بيئة الإنتاج الحقيقية، نضع رابط الموقع فقط هنا
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_EMPLOYEES = {
    "emp_001": {"name": "أحمد", "level": "A"},
    "emp_002": {"name": "سارة", "level": "C"},
}

def get_employee_level(employee_id: str):
    emp = DB_EMPLOYEES.get(employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="الموظف غير موجود في قاعدة البيانات")
    return emp["level"]

def verify_access(employee_level: str, required_level: str):
    levels = {'A': 3, 'B': 2, 'C': 1}
    # التحليل المنطقي الصارم للصلاحيات
    if levels.get(employee_level, 0) < levels.get(required_level, 0):
        raise HTTPException(status_code=403, detail="تم الرفض: صلاحياتك غير كافية للوصول لهذا المستوى من البيانات")

@app.get("/search/")
async def search_intelligence_brain(query: str, employee_id: str = "emp_002"):
    # ملاحظة: جعلنا emp_002 كقيمة افتراضية لأغراض الاختبار فقط
    
    current_level = get_employee_level(employee_id)
    
    # قائمة المصطلحات الحساسة
    sensitive_terms = ["عقد", "تمويل", "شركة x", "اتفاقية", "سري"]
    is_sensitive = False
    match_score = 0
    
    # تطبيق المنطق الضبابي
    for term in sensitive_terms:
        score = fuzz.partial_ratio(query, term)
        if score > 80: # درجة الانتماء (Degree of Membership) للمصطلحات الحساسة
            is_sensitive = True
            match_score = score
            break

    # اتخاذ القرار الصارم
    if is_sensitive:
        verify_access(current_level, "B")
        return {
            "status": "success",
            "message": "تم التحقق من الصلاحيات بنجاح.",
            "data": f"نتائج حساسة متعلقة بـ: {query}",
            "fuzzy_match_score": match_score
        }
    
    # في حال لم يكن البحث حساساً
    return {
        "status": "success",
        "message": "بحث عام",
        "data": f"نتائج عامة متعلقة بـ: {query}",
        "fuzzy_match_score": match_score
    }
