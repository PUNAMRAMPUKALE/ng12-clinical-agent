# app/api/assess.py

import logging
from fastapi import APIRouter, Depends, HTTPException

from app.domain.models import AssessRequest, AssessResponse
from app.config.container import Container
from app.api.deps import get_container

log = logging.getLogger("ng12")
router = APIRouter(prefix="/assess", tags=["assess"])


@router.post("", response_model=AssessResponse)
def assess(req: AssessRequest, c: Container = Depends(get_container)):
    try:
        return c.assessor_service.assess(req.patient_id, req.top_k)
    except KeyError:
        raise HTTPException(status_code=404, detail="Patient not found")
    except Exception:
        log.exception("Assess failed for patient_id=%s", req.patient_id)
        raise HTTPException(status_code=500, detail="Assessment failed. Check server logs.")
