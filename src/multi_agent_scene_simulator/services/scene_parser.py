"""
Advanced scene parser for extracting comprehensive scene state from Blender.

Replaces the simplistic parse_scene_info() with detailed structural analysis.
"""

import re
import json
from dataclasses import dataclass, asdict


@dataclass
class SceneObject:
    """Comprehensive object representation."""
    name: str
    object_type: str
    location: tuple[float, float, float]
    rotation: tuple[float, float, float]
    scale: tuple[float, float, float]
    dimensions: tuple[float, float, float]
    bounding_box: tuple[tuple[float, float, float], tuple[float, float, float]]
    vertex_count: int
    face_count: int
    edge_count: int
    materials: list[str]
    parent: str | None
    children: list[str]
    visibility: bool
    selectability: bool
    renderability: bool
    custom_properties: dict[str, object]


@dataclass
class SceneLight:
    """Detailed light representation."""
    name: str
    light_type: str  # POINT, SUN, SPOT, AREA
    location: tuple[float, float, float]
    rotation: tuple[float, float, float]
    energy: float
    color: tuple[float, float, float, float]
    temperature: float
    size: float
    spot_size: float | None
    spot_blend: float | None
    shadows: bool
    shadow_cascade: str
    light_group: str | None


@dataclass
class SceneCamera:
    """Detailed camera representation."""
    name: str
    location: tuple[float, float, float]
    rotation: tuple[float, float, float]
    focal_length: float
    sensor_width: float
    sensor_height: float
    clip_start: float
    clip_end: float
    dof_distance: float | None
    dof_fstop: float | None
    is_active: bool


@dataclass
class SceneMaterial:
    """Detailed material representation."""
    name: str
    base_color: tuple[float, float, float, float]
    metallic: float
    roughness: float
    specular: float
    emission: tuple[float, float, float, float]
    alpha: float
    normal_map: str | None
    texture_paths: list[str]
    is_procedural: bool
    node_count: int


@dataclass
class SceneState:
    """Complete scene state representation."""
    objects: list[SceneObject]
    lights: list[SceneLight]
    cameras: list[SceneCamera]
    materials: list[SceneMaterial]
    world_settings: dict[str, object]
    scene_dimensions: tuple[float, float, float]
    total_vertices: int
    total_faces: int
    total_objects: int
    render_engine: str
    unit_system: str
    frame_range: tuple[int, int]
    fps: float


class SceneParser:
    """Advanced scene parser for detailed state extraction."""
    
    def __init__(self):
        self.parsed_state = None
    
    def parse_scene_info(self, scene_info: str) -> SceneState:
        """
        Parse scene information into comprehensive SceneState.
        
        Args:
            scene_info: Raw scene information string from Blender
            
        Returns:
            Complete SceneState object with detailed scene information
        """
        try:
            # Try to parse as JSON first
            if self._is_json(scene_info):
                return self._parse_json_scene(scene_info)
            else:
                return self._parse_text_scene(scene_info)
        except Exception as e:
            # Fallback to basic parsing
            return self._fallback_parsing(scene_info)
    
    def _is_json(self, text: str) -> bool:
        """Check if text is valid JSON."""
        try:
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError):
            return False
    
    def _parse_json_scene(self, json_data: str) -> SceneState:
        """Parse JSON-formatted scene data."""
        data = json.loads(json_data)
        
        objects = []
        lights = []
        cameras = []
        materials = []
        
        # Parse objects
        for obj_data in data.get("objects", []):
            objects.append(SceneObject(
                name=obj_data.get("name", "unknown"),
                object_type=obj_data.get("type", "MESH"),
                location=self._tuple_from_list(obj_data.get("location", [0, 0, 0])),
                rotation=self._tuple_from_list(obj_data.get("rotation", [0, 0, 0])),
                scale=self._tuple_from_list(obj_data.get("scale", [1, 1, 1])),
                dimensions=self._tuple_from_list(obj_data.get("dimensions", [1, 1, 1])),
                bounding_box=self._parse_bounding_box(obj_data.get("bounding_box")),
                vertex_count=obj_data.get("vertex_count", 0),
                face_count=obj_data.get("face_count", 0),
                edge_count=obj_data.get("edge_count", 0),
                materials=obj_data.get("materials", []),
                parent=obj_data.get("parent"),
                children=obj_data.get("children", []),
                visibility=obj_data.get("visibility", True),
                selectability=obj_data.get("selectability", True),
                renderability=obj_data.get("renderability", True),
                custom_properties=obj_data.get("custom_properties", {})
            ))
        
        # Parse lights
        for light_data in data.get("lights", []):
            lights.append(SceneLight(
                name=light_data.get("name", "unknown"),
                light_type=light_data.get("type", "POINT"),
                location=self._tuple_from_list(light_data.get("location", [0, 0, 0])),
                rotation=self._tuple_from_list(light_data.get("rotation", [0, 0, 0])),
                energy=light_data.get("energy", 1.0),
                color=self._tuple_from_list(light_data.get("color", [1, 1, 1, 1])),
                temperature=light_data.get("temperature", 5500),
                size=light_data.get("size", 0.1),
                spot_size=light_data.get("spot_size"),
                spot_blend=light_data.get("spot_blend"),
                shadows=light_data.get("shadows", True),
                shadow_cascade=light_data.get("shadow_cascade", "NONE"),
                light_group=light_data.get("light_group")
            ))
        
        # Parse cameras
        for cam_data in data.get("cameras", []):
            cameras.append(SceneCamera(
                name=cam_data.get("name", "unknown"),
                location=self._tuple_from_list(cam_data.get("location", [0, 0, 0])),
                rotation=self._tuple_from_list(cam_data.get("rotation", [0, 0, 0])),
                focal_length=cam_data.get("focal_length", 50.0),
                sensor_width=cam_data.get("sensor_width", 36.0),
                sensor_height=cam_data.get("sensor_height", 24.0),
                clip_start=cam_data.get("clip_start", 0.1),
                clip_end=cam_data.get("clip_end", 1000.0),
                dof_distance=cam_data.get("dof_distance"),
                dof_fstop=cam_data.get("dof_fstop"),
                is_active=cam_data.get("is_active", True)
            ))
        
        # Parse materials
        for mat_data in data.get("materials", []):
            materials.append(SceneMaterial(
                name=mat_data.get("name", "unknown"),
                base_color=self._tuple_from_list(mat_data.get("base_color", [0.8, 0.8, 0.8, 1.0])),
                metallic=mat_data.get("metallic", 0.0),
                roughness=mat_data.get("roughness", 0.5),
                specular=mat_data.get("specular", 0.5),
                emission=self._tuple_from_list(mat_data.get("emission", [0, 0, 0, 1])),
                alpha=mat_data.get("alpha", 1.0),
                normal_map=mat_data.get("normal_map"),
                texture_paths=mat_data.get("texture_paths", []),
                is_procedural=mat_data.get("is_procedural", False),
                node_count=mat_data.get("node_count", 0)
            ))
        
        return SceneState(
            objects=objects,
            lights=lights,
            cameras=cameras,
            materials=materials,
            world_settings=data.get("world_settings", {}),
            scene_dimensions=self._tuple_from_list(data.get("scene_dimensions", [10, 10, 3])),
            total_vertices=data.get("total_vertices", 0),
            total_faces=data.get("total_faces", 0),
            total_objects=len(objects),
            render_engine=data.get("render_engine", "CYCLES"),
            unit_system=data.get("unit_system", "METRIC"),
            frame_range=(data.get("frame_start", 1), data.get("frame_end", 250)),
            fps=data.get("fps", 24.0)
        )
    
    def _parse_text_scene(self, text_data: str) -> SceneState:
        """Parse text-formatted scene data."""
        lines = text_data.split('\n')
        
        objects = []
        lights = []
        cameras = []
        materials = []
        
        current_object = None
        current_light = None
        current_camera = None
        current_material = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Object parsing
            if line.startswith('Object:') or line.startswith('- Object:'):
                if current_object:
                    objects.append(current_object)
                name = line.split('Object:')[-1].strip()
                current_object = SceneObject(
                    name=name,
                    object_type="MESH",
                    location=(0.0, 0.0, 0.0),
                    rotation=(0.0, 0.0, 0.0),
                    scale=(1.0, 1.0, 1.0),
                    dimensions=(1.0, 1.0, 1.0),
                    bounding_box=((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                    vertex_count=0,
                    face_count=0,
                    edge_count=0,
                    materials=[],
                    parent=None,
                    children=[],
                    visibility=True,
                    selectability=True,
                    renderability=True,
                    custom_properties={}
                )
            
            elif current_object and "Location:" in line:
                loc_str = line.split("Location:")[-1].strip()
                current_object.location = self._parse_vector(loc_str)
            
            elif current_object and "Rotation:" in line:
                rot_str = line.split("Rotation:")[-1].strip()
                current_object.rotation = self._parse_vector(rot_str)
            
            elif current_object and "Scale:" in line:
                scale_str = line.split("Scale:")[-1].strip()
                current_object.scale = self._parse_vector(scale_str)
            
            elif current_object and "Dimensions:" in line:
                dim_str = line.split("Dimensions:")[-1].strip()
                current_object.dimensions = self._parse_vector(dim_str)
            
            elif current_object and "Material:" in line:
                mat_name = line.split("Material:")[-1].strip()
                current_object.materials.append(mat_name)
            
            elif current_object and "Vertices:" in line:
                current_object.vertex_count = int(line.split("Vertices:")[-1].strip())
            
            elif current_object and "Faces:" in line:
                current_object.face_count = int(line.split("Faces:")[-1].strip())
            
            # Light parsing
            elif line.startswith('Light:') or line.startswith('- Light:'):
                if current_light:
                    lights.append(current_light)
                name = line.split('Light:')[-1].strip()
                current_light = SceneLight(
                    name=name,
                    light_type="POINT",
                    location=(0.0, 0.0, 0.0),
                    rotation=(0.0, 0.0, 0.0),
                    energy=1.0,
                    color=(1.0, 1.0, 1.0, 1.0),
                    temperature=5500.0,
                    size=0.1,
                    spot_size=None,
                    spot_blend=None,
                    shadows=True,
                    shadow_cascade="NONE",
                    light_group=None
                )
            
            elif current_light and "Energy:" in line:
                current_light.energy = float(line.split("Energy:")[-1].strip())
            
            elif current_light and "Color:" in line:
                color_str = line.split("Color:")[-1].strip()
                current_light.color = self._parse_color(color_str)
            
            # Camera parsing
            elif line.startswith('Camera:') or line.startswith('- Camera:'):
                if current_camera:
                    cameras.append(current_camera)
                name = line.split('Camera:')[-1].strip()
                current_camera = SceneCamera(
                    name=name,
                    location=(0.0, 0.0, 0.0),
                    rotation=(0.0, 0.0, 0.0),
                    focal_length=50.0,
                    sensor_width=36.0,
                    sensor_height=24.0,
                    clip_start=0.1,
                    clip_end=1000.0,
                    dof_distance=None,
                    dof_fstop=None,
                    is_active=True
                )
            
            elif current_camera and "Focal Length:" in line:
                current_camera.focal_length = float(line.split("Focal Length:")[-1].strip())
            
            elif current_camera and "Location:" in line:
                loc_str = line.split("Location:")[-1].strip()
                current_camera.location = self._parse_vector(loc_str)
        
        # Add last items
        if current_object:
            objects.append(current_object)
        if current_light:
            lights.append(current_light)
        if current_camera:
            cameras.append(current_camera)
        
        return SceneState(
            objects=objects,
            lights=lights,
            cameras=cameras,
            materials=materials,
            world_settings={},
            scene_dimensions=(10.0, 10.0, 3.0),
            total_vertices=sum(obj.vertex_count for obj in objects),
            total_faces=sum(obj.face_count for obj in objects),
            total_objects=len(objects),
            render_engine="CYCLES",
            unit_system="METRIC",
            frame_range=(1, 250),
            fps=24.0
        )
    
    def _fallback_parsing(self, scene_info: str) -> SceneState:
        """Basic fallback parsing for unknown formats."""
        lines = str(scene_info).split('\n')
        objects = []
        
        for line in lines:
            line = line.strip()
            if line and ('object' in line.lower() or 'Object:' in line):
                # Extract object name
                name = line.split(':')[-1].strip() if ':' in line else line
                objects.append(SceneObject(
                    name=name,
                    object_type="MESH",
                    location=(0.0, 0.0, 0.0),
                    rotation=(0.0, 0.0, 0.0),
                    scale=(1.0, 1.0, 1.0),
                    dimensions=(1.0, 1.0, 1.0),
                    bounding_box=((0.0, 0.0, 0.0), (1.0, 1.0, 1.0)),
                    vertex_count=0,
                    face_count=0,
                    edge_count=0,
                    materials=[],
                    parent=None,
                    children=[],
                    visibility=True,
                    selectability=True,
                    renderability=True,
                    custom_properties={}
                ))
        
        return SceneState(
            objects=objects,
            lights=[],
            cameras=[],
            materials=[],
            world_settings={},
            scene_dimensions=(10.0, 10.0, 3.0),
            total_vertices=0,
            total_faces=0,
            total_objects=len(objects),
            render_engine="CYCLES",
            unit_system="METRIC",
            frame_range=(1, 250),
            fps=24.0
        )
    
    def _tuple_from_list(self, lst: list) -> tuple[float, ...]:
        """Convert list to tuple with float conversion."""
        return tuple(float(x) for x in lst)
    
    def _parse_bounding_box(self, bbox_data: list | dict | None) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
        """Parse bounding box data."""
        if not bbox_data:
            return ((0.0, 0.0, 0.0), (1.0, 1.0, 1.0))
        
        if isinstance(bbox_data, dict):
            min_point = bbox_data.get("min", [0, 0, 0])
            max_point = bbox_data.get("max", [1, 1, 1])
        else:
            # Assume it's a list of two points
            min_point = bbox_data[0] if len(bbox_data) > 0 else [0, 0, 0]
            max_point = bbox_data[1] if len(bbox_data) > 1 else [1, 1, 1]
        
        return (tuple(float(x) for x in min_point), tuple(float(x) for x in max_point))
    
    def _parse_vector(self, vector_str: str) -> tuple[float, float, float]:
        """Parse vector string to tuple."""
        try:
            # Handle formats like "(1.0, 2.0, 3.0)" or "1.0, 2.0, 3.0"
            cleaned = vector_str.strip('()[]')
            parts = [float(x.strip()) for x in cleaned.split(',')]
            return tuple(parts[:3]) if len(parts) >= 3 else (0.0, 0.0, 0.0)
        except (ValueError, IndexError):
            return (0.0, 0.0, 0.0)
    
    def _parse_color(self, color_str: str) -> tuple[float, float, float, float]:
        """Parse color string to RGBA tuple."""
        try:
            # Handle formats like "(1.0, 1.0, 1.0, 1.0)" or "1.0, 1.0, 1.0, 1.0"
            cleaned = color_str.strip('()[]')
            parts = [float(x.strip()) for x in cleaned.split(',')]
            if len(parts) == 3:
                return (parts[0], parts[1], parts[2], 1.0)
            elif len(parts) == 4:
                return tuple(parts)
            else:
                return (1.0, 1.0, 1.0, 1.0)
        except (ValueError, IndexError):
            return (1.0, 1.0, 1.0, 1.0)
    
    def scene_state_to_dict(self, scene_state: SceneState) -> dict[str, object]:
        """Convert SceneState to dictionary for JSON serialization."""
        return {
            "objects": [asdict(obj) for obj in scene_state.objects],
            "lights": [asdict(light) for light in scene_state.lights],
            "cameras": [asdict(cam) for cam in scene_state.cameras],
            "materials": [asdict(mat) for mat in scene_state.materials],
            "world_settings": scene_state.world_settings,
            "scene_dimensions": scene_state.scene_dimensions,
            "total_vertices": scene_state.total_vertices,
            "total_faces": scene_state.total_faces,
            "total_objects": scene_state.total_objects,
            "render_engine": scene_state.render_engine,
            "unit_system": scene_state.unit_system,
            "frame_range": scene_state.frame_range,
            "fps": scene_state.fps
        }