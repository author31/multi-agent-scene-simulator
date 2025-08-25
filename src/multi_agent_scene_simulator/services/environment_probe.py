"""
Comprehensive scene analysis engine for detailed environmental feedback.

This module provides deep analysis of Blender scenes to enable precise
scene matching and intelligent refinement based on user requirements.
"""

import math
import re
from dataclasses import dataclass


@dataclass
class ObjectMetrics:
    """Detailed metrics for a single object."""
    name: str
    object_type: str
    position: tuple[float, float, float]
    dimensions: tuple[float, float, float]  # exact bounding box
    volume: float
    surface_area: float
    material_count: int
    vertex_count: int
    face_count: int
    is_manifold: bool
    normal_consistency: float


@dataclass
class LightingMetrics:
    """Comprehensive lighting analysis."""
    light_count: int
    total_lumens: float
    color_temperatures: list[float]
    shadow_softness: float
    light_distribution: dict[str, float]  # by zone
    contrast_ratio: float
    average_illuminance: float
    darkest_point: float
    brightest_point: float


@dataclass
class SpatialMetrics:
    """Spatial relationships and layout analysis."""
    room_dimensions: tuple[float, float, float]
    usable_volume: float
    object_density: float
    traffic_flow_score: float
    functional_zones: dict[str, dict[str, object]]
    object_distances: dict[str, dict[str, float]]
    alignment_consistency: float
    proportional_balance: float


@dataclass
class AestheticMetrics:
    """Visual and style analysis."""
    color_palette: list[str]
    color_harmony_score: float
    style_consistency: float
    visual_balance: float
    focal_point_strength: float
    material_coherence: float
    texture_variety: float
    overall_atmosphere: str


class EnvironmentProbe:
    """Deep analysis engine for Blender scene state."""
    
    def __init__(self):
        self.scene_state = {}
        self.analysis_cache = {}
    
    def analyze_complete_scene(self, scene_info: str, screenshot_path: str = None) -> dict[str, object]:
        """
        Perform comprehensive scene analysis.
        
        Args:
            scene_info: Raw scene information from Blender
            screenshot_path: Optional path to viewport screenshot
            
        Returns:
            Complete scene analysis with all metrics
        """
        try:
            # Parse basic scene structure
            basic_objects = self._parse_scene_objects(scene_info)
            
            # Analyze each object in detail
            object_metrics = self._analyze_object_metrics(basic_objects)
            
            # Analyze lighting conditions
            lighting_metrics = self._analyze_lighting_metrics(basic_objects)
            
            # Analyze spatial relationships
            spatial_metrics = self._analyze_spatial_metrics(object_metrics)
            
            # Analyze aesthetic properties
            aesthetic_metrics = self._analyze_aesthetic_metrics(object_metrics, lighting_metrics)
            
            return {
                "objects": object_metrics,
                "lighting": lighting_metrics,
                "spatial": spatial_metrics,
                "aesthetic": aesthetic_metrics,
                "summary": self._generate_summary(object_metrics, lighting_metrics, spatial_metrics, aesthetic_metrics),
                "issues": self._identify_issues(object_metrics, lighting_metrics, spatial_metrics, aesthetic_metrics),
                "recommendations": self._generate_recommendations(object_metrics, lighting_metrics, spatial_metrics, aesthetic_metrics)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "objects": [],
                "lighting": None,
                "spatial": None,
                "aesthetic": None,
                "summary": {},
                "issues": ["Analysis failed"],
                "recommendations": ["Retry analysis"]
            }
    
    def _parse_scene_objects(self, scene_info: str) -> list[dict[str, object]]:
        """Parse scene info to extract object details."""
        objects = []
        
        if isinstance(scene_info, str):
            lines = scene_info.split('\n')
            current_object = None
            
            for line in lines:
                line = line.strip()
                
                # Object detection
                if line.startswith('Object:') or line.startswith('- Object:'):
                    if current_object:
                        objects.append(current_object)
                    
                    name = line.split('Object:')[-1].strip()
                    current_object = {
                        "name": name,
                        "type": "unknown",
                        "location": (0.0, 0.0, 0.0),
                        "dimensions": (1.0, 1.0, 1.0),
                        "materials": [],
                        "properties": {}
                    }
                
                elif current_object:
                    # Parse object properties
                    if "Location:" in line:
                        loc_str = line.split("Location:")[-1].strip()
                        current_object["location"] = self._parse_vector(loc_str)
                    elif "Dimensions:" in line:
                        dim_str = line.split("Dimensions:")[-1].strip()
                        current_object["dimensions"] = self._parse_vector(dim_str)
                    elif "Type:" in line:
                        current_object["type"] = line.split("Type:")[-1].strip()
                    elif "Material:" in line:
                        current_object["materials"].append(line.split("Material:")[-1].strip())
        
        if current_object:
            objects.append(current_object)
        
        return objects
    
    def _analyze_object_metrics(self, objects: list[dict[str, object]]) -> list[ObjectMetrics]:
        """Analyze detailed object properties."""
        metrics = []
        
        for obj in objects:
            name = obj.get("name", "unknown")
            obj_type = obj.get("type", "unknown")
            position = obj.get("location", (0.0, 0.0, 0.0))
            dimensions = obj.get("dimensions", (1.0, 1.0, 1.0))
            
            # Calculate derived metrics
            volume = dimensions[0] * dimensions[1] * dimensions[2]
            surface_area = 2 * (dimensions[0] * dimensions[1] + dimensions[1] * dimensions[2] + dimensions[2] * dimensions[0])
            
            # Estimate complexity based on object type
            material_count = len(obj.get("materials", []))
            vertex_count = self._estimate_vertex_count(obj_type, dimensions)
            face_count = self._estimate_face_count(obj_type, dimensions)
            
            # Quality metrics (simplified estimation)
            is_manifold = True  # Assume valid unless proven otherwise
            normal_consistency = 1.0  # Perfect normals for basic objects
            
            metrics.append(ObjectMetrics(
                name=name,
                object_type=obj_type,
                position=position,
                dimensions=dimensions,
                volume=volume,
                surface_area=surface_area,
                material_count=material_count,
                vertex_count=vertex_count,
                face_count=face_count,
                is_manifold=is_manifold,
                normal_consistency=normal_consistency
            ))
        
        return metrics
    
    def _analyze_lighting_metrics(self, objects: list[dict[str, object]]) -> LightingMetrics:
        """Analyze lighting conditions in the scene."""
        lights = [obj for obj in objects if "light" in obj.get("type", "").lower()]
        
        light_count = len(lights)
        total_lumens = 0.0
        color_temperatures = []
        
        for light in lights:
            # Estimate lighting properties based on type
            if "sun" in light.get("type", "").lower():
                total_lumens += 100000  # Sun-like intensity
                color_temperatures.append(5500)  # Daylight
            elif "point" in light.get("type", "").lower():
                total_lumens += 800  # Typical bulb
                color_temperatures.append(2700)  # Warm white
            elif "area" in light.get("type", "").lower():
                total_lumens += 2000  # Panel light
                color_temperatures.append(4000)  # Neutral white
        
        # Calculate lighting quality metrics
        shadow_softness = 0.7  # Simplified estimation
        contrast_ratio = 3.0  # Simplified estimation
        average_illuminance = total_lumens / 20.0  # Rough room estimation
        darkest_point = average_illuminance * 0.1
        brightest_point = average_illuminance * 3.0
        
        # Light distribution by zone (simplified)
        light_distribution = {
            "general": total_lumens * 0.6,
            "task": total_lumens * 0.3,
            "accent": total_lumens * 0.1
        }
        
        return LightingMetrics(
            light_count=light_count,
            total_lumens=total_lumens,
            color_temperatures=color_temperatures,
            shadow_softness=shadow_softness,
            light_distribution=light_distribution,
            contrast_ratio=contrast_ratio,
            average_illuminance=average_illuminance,
            darkest_point=darkest_point,
            brightest_point=brightest_point
        )
    
    def _analyze_spatial_metrics(self, object_metrics: list[ObjectMetrics]) -> SpatialMetrics:
        """Analyze spatial relationships and layout."""
        if not object_metrics:
            return SpatialMetrics(
                room_dimensions=(0.0, 0.0, 0.0),
                usable_volume=0.0,
                object_density=0.0,
                traffic_flow_score=0.0,
                functional_zones={},
                object_distances={},
                alignment_consistency=0.0,
                proportional_balance=0.0
            )
        
        # Calculate room dimensions based on object bounds
        all_positions = [obj.position for obj in object_metrics]
        all_dimensions = [obj.dimensions for obj in object_metrics]
        
        if not all_positions:
            return SpatialMetrics(
                room_dimensions=(10.0, 10.0, 3.0),
                usable_volume=300.0,
                object_density=0.0,
                traffic_flow_score=0.5,
                functional_zones={},
                object_distances={},
                alignment_consistency=0.5,
                proportional_balance=0.5
            )
        
        # Calculate room bounds
        min_x = min(pos[0] - dim[0]/2 for pos, dim in zip(all_positions, all_dimensions))
        max_x = max(pos[0] + dim[0]/2 for pos, dim in zip(all_positions, all_dimensions))
        min_y = min(pos[1] - dim[1]/2 for pos, dim in zip(all_positions, all_dimensions))
        max_y = max(pos[1] + dim[1]/2 for pos, dim in zip(all_positions, all_dimensions))
        min_z = min(pos[2] - dim[2]/2 for pos, dim in zip(all_positions, all_dimensions))
        max_z = max(pos[2] + dim[2]/2 for pos, dim in zip(all_positions, all_dimensions))
        
        room_dimensions = (
            max(max_x - min_x, 5.0),  # Minimum 5m
            max(max_y - min_y, 5.0),  # Minimum 5m
            max(max_z - min_z, 2.5)  # Minimum 2.5m ceiling
        )
        
        usable_volume = room_dimensions[0] * room_dimensions[1] * room_dimensions[2]
        total_object_volume = sum(obj.volume for obj in object_metrics)
        object_density = total_object_volume / usable_volume if usable_volume > 0 else 0.0
        
        # Traffic flow score (simplified)
        traffic_flow_score = max(0.1, 1.0 - object_density)
        
        # Functional zones (simplified estimation)
        functional_zones = self._identify_functional_zones(object_metrics)
        
        # Object distances
        object_distances = self._calculate_object_distances(object_metrics)
        
        # Alignment and proportion scores
        alignment_consistency = self._calculate_alignment_consistency(object_metrics)
        proportional_balance = self._calculate_proportional_balance(object_metrics)
        
        return SpatialMetrics(
            room_dimensions=room_dimensions,
            usable_volume=usable_volume,
            object_density=object_density,
            traffic_flow_score=traffic_flow_score,
            functional_zones=functional_zones,
            object_distances=object_distances,
            alignment_consistency=alignment_consistency,
            proportional_balance=proportional_balance
        )
    
    def _analyze_aesthetic_metrics(self, object_metrics: list[ObjectMetrics], lighting_metrics: LightingMetrics) -> AestheticMetrics:
        """Analyze aesthetic and style properties."""
        # Simplified aesthetic analysis
        color_palette = ["neutral", "warm", "modern"]  # Placeholder
        color_harmony_score = 0.8  # Simplified
        style_consistency = 0.75  # Simplified
        visual_balance = 0.7  # Simplified
        focal_point_strength = 0.6  # Simplified
        material_coherence = 0.8  # Simplified
        texture_variety = 0.6  # Simplified
        overall_atmosphere = "cozy modern"  # Placeholder
        
        return AestheticMetrics(
            color_palette=color_palette,
            color_harmony_score=color_harmony_score,
            style_consistency=style_consistency,
            visual_balance=visual_balance,
            focal_point_strength=focal_point_strength,
            material_coherence=material_coherence,
            texture_variety=texture_variety,
            overall_atmosphere=overall_atmosphere
        )
    
    def _generate_summary(self, objects, lighting, spatial, aesthetic) -> dict[str, object]:
        """Generate high-level summary of scene state."""
        return {
            "total_objects": len(objects),
            "total_lights": lighting.light_count,
            "room_size": spatial.room_dimensions,
            "object_density": spatial.object_density,
            "lighting_quality": "adequate" if lighting.average_illuminance > 100 else "poor",
            "style_consistency": aesthetic.style_consistency,
            "functional_completeness": len(spatial.functional_zones),
            "overall_score": (aesthetic.style_consistency + spatial.proportional_balance + lighting.average_illuminance / 500.0) / 3.0
        }
    
    def _identify_issues(self, objects, lighting, spatial, aesthetic) -> list[str]:
        """Identify specific issues with the current scene."""
        issues = []
        
        # Lighting issues
        if lighting.average_illuminance < 100.0:
            issues.append("Insufficient lighting")
        if lighting.contrast_ratio > 10.0:
            issues.append("Lighting contrast too high")
        
        # Spatial issues
        if spatial.object_density > 0.3:
            issues.append("Scene too cluttered")
        if spatial.traffic_flow_score < 0.5:
            issues.append("Poor traffic flow")
        
        # Aesthetic issues
        if aesthetic.style_consistency < 0.6:
            issues.append("Inconsistent style")
        if aesthetic.visual_balance < 0.5:
            issues.append("Poor visual balance")
        
        return issues
    
    def _generate_recommendations(self, objects, lighting, spatial, aesthetic) -> list[str]:
        """Generate specific recommendations for improvement."""
        recommendations = []
        
        # Lighting recommendations
        if lighting.average_illuminance < 100.0:
            recommendations.append("Add ambient lighting")
        if lighting.light_count < 2:
            recommendations.append("Add task lighting")
        
        # Spatial recommendations
        if spatial.object_density > 0.3:
            recommendations.append("Reduce object density")
        if len(spatial.functional_zones) < 3:
            recommendations.append("Define more functional zones")
        
        # Aesthetic recommendations
        if aesthetic.style_consistency < 0.6:
            recommendations.append("Unify material styles")
        
        return recommendations
    
    def _parse_vector(self, vector_str: str) -> tuple[float, float, float]:
        """Parse vector string to tuple."""
        try:
            # Handle formats like "(1.0, 2.0, 3.0)" or "1.0, 2.0, 3.0"
            cleaned = vector_str.strip('()[]')
            parts = [float(x.strip()) for x in cleaned.split(',')]
            return tuple(parts[:3]) if len(parts) >= 3 else (0.0, 0.0, 0.0)
        except (ValueError, IndexError):
            return (0.0, 0.0, 0.0)
    
    def _estimate_vertex_count(self, obj_type: str, dimensions: tuple[float, float, float]) -> int:
        """Estimate vertex count based on object type and size."""
        base_vertices = {
            "cube": 8,
            "sphere": 32,
            "cylinder": 24,
            "plane": 4,
            "monkey": 500  # Suzanne
        }
        
        base = base_vertices.get(obj_type.lower(), 8)
        size_factor = sum(dimensions) / 3.0  # Average dimension
        return int(base * max(1.0, size_factor))
    
    def _estimate_face_count(self, obj_type: str, dimensions: tuple[float, float, float]) -> int:
        """Estimate face count based on object type and size."""
        base_faces = {
            "cube": 6,
            "sphere": 32,
            "cylinder": 12,
            "plane": 1,
            "monkey": 500
        }
        
        base = base_faces.get(obj_type.lower(), 6)
        size_factor = sum(dimensions) / 3.0
        return int(base * max(1.0, size_factor))
    
    def _identify_functional_zones(self, objects: list[ObjectMetrics]) -> dict[str, dict[str, object]]:
        """Identify functional zones based on object types and positions."""
        zones = {}
        
        # Simple zone identification based on object types and positions
        for obj in objects:
            obj_name = obj.name.lower()
            
            # Kitchen zone
            if any(kw in obj_name for kw in ["table", "chair", "counter", "stove", "sink"]):
                zones.setdefault("kitchen", {"objects": [], "center": (0.0, 0.0, 0.0)})
                zones["kitchen"]["objects"].append(obj.name)
            
            # Living zone
            elif any(kw in obj_name for kw in ["sofa", "couch", "tv", "television", "coffee"]):
                zones.setdefault("living", {"objects": [], "center": (0.0, 0.0, 0.0)})
                zones["living"]["objects"].append(obj.name)
            
            # Sleeping zone
            elif any(kw in obj_name for kw in ["bed", "nightstand", "lamp"]):
                zones.setdefault("bedroom", {"objects": [], "center": (0.0, 0.0, 0.0)})
                zones["bedroom"]["objects"].append(obj.name)
        
        return zones
    
    def _calculate_object_distances(self, objects: list[ObjectMetrics]) -> dict[str, dict[str, float]]:
        """Calculate distances between objects."""
        distances = {}
        
        for i, obj1 in enumerate(objects):
            distances[obj1.name] = {}
            for j, obj2 in enumerate(objects):
                if i != j:
                    dist = math.sqrt(
                        (obj1.position[0] - obj2.position[0]) ** 2 +
                        (obj1.position[1] - obj2.position[1]) ** 2 +
                        (obj1.position[2] - obj2.position[2]) ** 2
                    )
                    distances[obj1.name][obj2.name] = dist
        
        return distances
    
    def _calculate_alignment_consistency(self, objects: list[ObjectMetrics]) -> float:
        """Calculate how well objects are aligned."""
        if len(objects) < 2:
            return 1.0
        
        # Check for axis alignment consistency
        positions = [obj.position for obj in objects]
        
        # Calculate variance in each axis
        x_variance = sum((pos[0] - sum(p[0] for p in positions) / len(positions)) ** 2 for pos in positions)
        y_variance = sum((pos[1] - sum(p[1] for p in positions) / len(positions)) ** 2 for pos in positions)
        z_variance = sum((pos[2] - sum(p[2] for p in positions) / len(positions)) ** 2 for pos in positions)
        
        # Normalize variance (lower is better)
        max_variance = max(x_variance, y_variance, z_variance) + 1e-6
        alignment_score = 1.0 - (max_variance / (max_variance + 1.0))
        
        return max(0.0, min(1.0, alignment_score))
    
    def _calculate_proportional_balance(self, objects: list[ObjectMetrics]) -> float:
        """Calculate visual balance based on object proportions."""
        if len(objects) < 2:
            return 1.0
        
        # Calculate volume distribution
        volumes = [obj.volume for obj in objects]
        total_volume = sum(volumes)
        
        if total_volume == 0:
            return 1.0
        
        # Calculate balance based on volume distribution
        avg_volume = total_volume / len(volumes)
        volume_variance = sum((v - avg_volume) ** 2 for v in volumes) / len(volumes)
        
        # Normalize to 0-1 scale
        max_variance = avg_volume ** 2 + 1e-6
        balance_score = 1.0 - (volume_variance / max_variance)
        
        return max(0.0, min(1.0, balance_score))