from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional, List
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Product
import os

router = APIRouter()

class ProductBase(BaseModel):
    name: str
    description: str
    price: Decimal
    stock: int
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    image: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True

@router.get("/products/", response_model=List[ProductResponse])
async def get_products():
    products = Product.objects.all()
    return list(products)

@router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int):
    try:
        product = Product.objects.get(id=product_id)
        return product
    except Product.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")

@router.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate, image: UploadFile = File(...)):
    try:
        # Save image
        file_name = f"products/{image.filename}"
        path = default_storage.save(file_name, ContentFile(await image.read()))
        
        # Create product
        db_product = Product.objects.create(
            **product.dict(),
            image=path
        )
        return db_product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/products/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    image: Optional[UploadFile] = File(None)
):
    try:
        db_product = Product.objects.get(id=product_id)
        
        # Update image if provided
        if image:
            if db_product.image:
                # Delete old image
                if os.path.exists(db_product.image.path):
                    os.remove(db_product.image.path)
            
            file_name = f"products/{image.filename}"
            path = default_storage.save(file_name, ContentFile(await image.read()))
            db_product.image = path
        
        # Update other fields
        for field, value in product.dict().items():
            setattr(db_product, field, value)
        
        db_product.save()
        return db_product
    except Product.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(product_id: int):
    try:
        product = Product.objects.get(id=product_id)
        
        # Delete image file
        if product.image and os.path.exists(product.image.path):
            os.remove(product.image.path)
        
        product.delete()
        return {"message": "Product deleted successfully"}
    except Product.DoesNotExist:
        raise HTTPException(status_code=404, detail="Product not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) 