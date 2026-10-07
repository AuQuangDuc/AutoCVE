"""
数据库初始化模块
在应用启动时创建默认演示账户和演示数据
"""
import json
import logging
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash
from app.models.user import User
from app.models.project import Project, ProjectMember
from app.models.audit import AuditTask, AuditIssue
from app.models.analysis import InstantAnalysis

logger = logging.getLogger(__name__)

# 默认演示账户配置
DEFAULT_DEMO_EMAIL = "demo@example.com"
DEFAULT_DEMO_PASSWORD = "demo123"
DEFAULT_DEMO_NAME = "Người dùng demo"


async def create_demo_user(db: AsyncSession) -> User | None:
    """
    创建演示用户账户
    - demo@example.com / demo123
    """
    result = await db.execute(select(User).where(User.email == DEFAULT_DEMO_EMAIL))
    demo_user = result.scalars().first()
    
    if not demo_user:
        demo_user = User(
            email=DEFAULT_DEMO_EMAIL,
            hashed_password=get_password_hash(DEFAULT_DEMO_PASSWORD),
            full_name=DEFAULT_DEMO_NAME,
            is_active=True,
            is_superuser=True,  # 演示用户拥有管理员权限以便体验所有功能
            role="admin",
        )
        db.add(demo_user)
        await db.flush()
        logger.info(f"✓ 创建演示账户: {DEFAULT_DEMO_EMAIL}")
        return demo_user
    else:
        logger.info(f"演示账户已存在: {DEFAULT_DEMO_EMAIL}")
        return demo_user


async def create_demo_data(db: AsyncSession, user: User) -> None:
    """
    为演示用户创建演示数据，用于仪表盘展示
    """
    # 检查是否已有演示数据
    result = await db.execute(select(Project).where(Project.owner_id == user.id))
    existing_projects = result.scalars().all()
    if existing_projects:
        logger.info("演示数据已存在，跳过创建")
        return
    
    logger.info("开始创建演示数据...")
    now = datetime.now(timezone.utc)
    
    # ==================== 创建演示项目 ====================
    projects_data = [
        {
            "name": "Backend nền tảng thương mại điện tử",
            "description": "Dịch vụ backend thương mại điện tử dựa trên Spring Boot, gồm quản lý người dùng, sản phẩm và xử lý đơn hàng",
            "source_type": "repository",
            "repository_url": "https://github.com/example/ecommerce-backend",
            "repository_type": "github",
            "default_branch": "main",
            "programming_languages": json.dumps(["Java", "SQL"]),
        },
        {
            "name": "Ứng dụng di động",
            "description": "Ứng dụng di động đa nền tảng React Native, hỗ trợ iOS và Android",
            "source_type": "repository",
            "repository_url": "https://github.com/example/mobile-app",
            "repository_type": "github",
            "default_branch": "develop",
            "programming_languages": json.dumps(["TypeScript", "JavaScript"]),
        },
        {
            "name": "Nền tảng phân tích dữ liệu",
            "description": "Nền tảng phân tích và trực quan hóa dữ liệu Python, tích hợp mô hình machine learning",
            "source_type": "zip",
            "repository_url": None,
            "repository_type": "other",
            "default_branch": "main",
            "programming_languages": json.dumps(["Python"]),
        },
        {
            "name": "API Gateway microservice",
            "description": "API Gateway hiệu năng cao viết bằng Go, hỗ trợ rate limiting, circuit breaker và cân bằng tải",
            "source_type": "repository",
            "repository_url": "https://gitlab.com/example/api-gateway",
            "repository_type": "gitlab",
            "default_branch": "master",
            "programming_languages": json.dumps(["Go"]),
        },
        {
            "name": "Hệ thống chăm sóc khách hàng thông minh",
            "description": "Hệ thống chăm sóc khách hàng dựa trên NLP, hỗ trợ hội thoại nhiều lượt, nhận diện ý định và hỏi đáp kho tri thức",
            "source_type": "repository",
            "repository_url": "https://github.com/example/smart-customer-service",
            "repository_type": "github",
            "default_branch": "main",
            "programming_languages": json.dumps(["Python", "JavaScript"]),
        },
        {
            "name": "Ví blockchain",
            "description": "Ví tiền mã hóa đa chuỗi, hỗ trợ lưu trữ và chuyển ETH, BTC cùng các tài sản phổ biến khác",
            "source_type": "zip",
            "repository_url": None,
            "repository_type": "other",
            "default_branch": "main",
            "programming_languages": json.dumps(["Rust", "TypeScript"]),
        },
    ]
    
    projects = []
    for i, pdata in enumerate(projects_data):
        project = Project(
            owner_id=user.id,
            is_active=True,
            created_at=now - timedelta(days=30 - i * 5),
            **pdata
        )
        db.add(project)
        projects.append(project)
    
    await db.flush()
    logger.info(f"✓ 创建了 {len(projects)} 个演示项目")
    
    # ==================== 创建审计任务和问题 ====================
    tasks_data = [
        # 项目1: 电商平台后端
        {"project_idx": 0, "status": "completed", "days_ago": 25, "files": 156, "lines": 12500, "issues": 23, "score": 72.5},
        {"project_idx": 0, "status": "completed", "days_ago": 15, "files": 162, "lines": 13200, "issues": 18, "score": 78.3},
        {"project_idx": 0, "status": "completed", "days_ago": 5, "files": 168, "lines": 14100, "issues": 12, "score": 85.2},
        # 项目2: 移动端 App
        {"project_idx": 1, "status": "completed", "days_ago": 20, "files": 89, "lines": 8900, "issues": 15, "score": 68.7},
        {"project_idx": 1, "status": "completed", "days_ago": 8, "files": 95, "lines": 9500, "issues": 8, "score": 82.1},
        {"project_idx": 1, "status": "completed", "days_ago": 1, "files": 98, "lines": 9800, "issues": 6, "score": 84.5},
        # 项目3: 数据分析平台
        {"project_idx": 2, "status": "completed", "days_ago": 12, "files": 45, "lines": 5600, "issues": 9, "score": 76.4},
        {"project_idx": 2, "status": "completed", "days_ago": 2, "files": 52, "lines": 6200, "issues": 5, "score": 88.9},
        # 项目4: 微服务网关
        {"project_idx": 3, "status": "completed", "days_ago": 18, "files": 78, "lines": 9200, "issues": 11, "score": 74.8},
        {"project_idx": 3, "status": "failed", "days_ago": 3, "files": 0, "lines": 0, "issues": 0, "score": 0},
        # 项目5: 智能客服系统
        {"project_idx": 4, "status": "completed", "days_ago": 22, "files": 134, "lines": 15800, "issues": 19, "score": 71.2},
        {"project_idx": 4, "status": "completed", "days_ago": 10, "files": 142, "lines": 16500, "issues": 14, "score": 79.6},
        {"project_idx": 4, "status": "completed", "days_ago": 1, "files": 148, "lines": 17200, "issues": 7, "score": 86.8},
        # 项目6: 区块链钱包
        {"project_idx": 5, "status": "completed", "days_ago": 16, "files": 67, "lines": 8400, "issues": 16, "score": 65.3},
        {"project_idx": 5, "status": "completed", "days_ago": 6, "files": 72, "lines": 9100, "issues": 9, "score": 77.5},
    ]
    
    tasks = []
    for tdata in tasks_data:
        task_time = now - timedelta(days=tdata["days_ago"])
        task = AuditTask(
            project_id=projects[tdata["project_idx"]].id,
            created_by=user.id,
            task_type="full_scan",
            status=tdata["status"],
            branch_name="main",
            total_files=tdata["files"],
            scanned_files=tdata["files"] if tdata["status"] == "completed" else 0,
            total_lines=tdata["lines"],
            issues_count=tdata["issues"],
            quality_score=tdata["score"],
            started_at=task_time,
            completed_at=task_time + timedelta(minutes=5) if tdata["status"] == "completed" else None,
            created_at=task_time,
        )
        db.add(task)
        tasks.append(task)
    
    await db.flush()
    logger.info(f"✓ 创建了 {len(tasks)} 个审计任务")
    
    # ==================== 创建审计问题 ====================
    issue_templates = [
        {"type": "security", "severity": "critical", "title": "Lỗ hổng SQL Injection", "file": "UserService.java", "line": 45},
        {"type": "security", "severity": "high", "title": "Khóa bí mật hard-code", "file": "config/secrets.py", "line": 12},
        {"type": "security", "severity": "high", "title": "Rủi ro Cross-Site Scripting (XSS)", "file": "components/Comment.tsx", "line": 78},
        {"type": "security", "severity": "medium", "title": "Sinh số ngẫu nhiên không an toàn", "file": "utils/token.go", "line": 23},
        {"type": "bug", "severity": "high", "title": "Rủi ro null pointer", "file": "OrderController.java", "line": 156},
        {"type": "bug", "severity": "medium", "title": "Truy cập vượt giới hạn mảng", "file": "DataProcessor.py", "line": 89},
        {"type": "bug", "severity": "low", "title": "Promise rejection chưa được xử lý", "file": "api/client.ts", "line": 34},
        {"type": "performance", "severity": "medium", "title": "Vấn đề truy vấn N+1", "file": "ProductRepository.java", "line": 67},
        {"type": "performance", "severity": "low", "title": "Render lặp không cần thiết", "file": "pages/Dashboard.tsx", "line": 112},
        {"type": "style", "severity": "low", "title": "Hàm quá dài, nên tách nhỏ", "file": "services/payment.go", "line": 45},
        {"type": "maintainability", "severity": "medium", "title": "Khối mã bị lặp", "file": "handlers/auth.go", "line": 78},
        {"type": "maintainability", "severity": "low", "title": "Thiếu xử lý lỗi", "file": "utils/http.py", "line": 56},
    ]
    
    issue_count = 0
    for task in tasks:
        if task.status != "completed" or task.issues_count == 0:
            continue
        
        # 为每个完成的任务创建问题
        num_issues = min(task.issues_count, len(issue_templates))
        for i in range(num_issues):
            template = issue_templates[i % len(issue_templates)]
            issue = AuditIssue(
                task_id=task.id,
                file_path=f"src/{template['file']}",
                line_number=template["line"] + i * 10,
                issue_type=template["type"],
                severity=template["severity"],
                title=template["title"],
                message=template["title"],
                description=f"Phát hiện {template['title']} tại tệp {template['file']}, dòng {template['line'] + i * 10}; vấn đề này có thể gây rủi ro bảo mật hoặc lỗi chương trình.",
                suggestion="Khuyến nghị rà soát mã nguồn và khắc phục vấn đề này. Tham khảo tiêu chuẩn bảo mật liên quan để có phương án chi tiết.",
                status="open" if i % 3 != 0 else "resolved",
                resolved_by=user.id if i % 3 == 0 else None,
                resolved_at=now - timedelta(days=i) if i % 3 == 0 else None,
                created_at=task.created_at,
            )
            db.add(issue)
            issue_count += 1
    
    await db.flush()
    logger.info(f"✓ 创建了 {issue_count} 个审计问题")
    
    # ==================== 创建即时分析记录 ====================
    analyses_data = [
        {"lang": "Python", "issues": 3, "score": 75.5, "days_ago": 10},
        {"lang": "JavaScript", "issues": 5, "score": 68.2, "days_ago": 8},
        {"lang": "Java", "issues": 2, "score": 82.1, "days_ago": 6},
        {"lang": "Go", "issues": 1, "score": 91.3, "days_ago": 4},
        {"lang": "TypeScript", "issues": 4, "score": 72.8, "days_ago": 2},
        {"lang": "Python", "issues": 0, "score": 95.0, "days_ago": 1},
    ]
    
    for adata in analyses_data:
        analysis = InstantAnalysis(
            user_id=user.id,
            language=adata["lang"],
            code_content="# Mã demo\nprint('Hello, World!')",
            analysis_result=json.dumps({"issues": [], "summary": "Kết quả phân tích demo"}),
            issues_count=adata["issues"],
            quality_score=adata["score"],
            analysis_time=2.5,
            created_at=now - timedelta(days=adata["days_ago"]),
        )
        db.add(analysis)
    
    await db.flush()
    logger.info(f"✓ 创建了 {len(analyses_data)} 条即时分析记录")
    
    await db.commit()
    logger.info("✓ 演示数据创建完成")


async def init_db(db: AsyncSession) -> None:
    """
    初始化数据库
    """
    logger.info("开始初始化数据库...")
    
    # 创建演示用户
    demo_user = await create_demo_user(db)
    
    # 创建演示数据
    if demo_user:
        await create_demo_data(db, demo_user)
    
    await db.commit()
    
    # 初始化系统模板和规则
    try:
        from app.services.init_templates import init_templates_and_rules
        await init_templates_and_rules(db)
    except Exception as e:
        logger.warning(f"????????????: {e}")

    # ??? Agent Skills ?????
    try:
        from app.services.init_agent_assets import init_agent_assets
        await init_agent_assets(db)
    except Exception as e:
        logger.warning(f"初始化模板和规则跳过: {e}")
    
    logger.info("数据库初始化完成")
