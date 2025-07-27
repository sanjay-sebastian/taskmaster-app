from flask import Blueprint, jsonify, request
from datetime import datetime, date
from src.models.task import Task, db

task_bp = Blueprint('task', __name__)

@task_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get all tasks with optional filtering"""
    # Get query parameters for filtering
    status = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    search = request.args.get('search')
    
    # Start with all tasks
    query = Task.query
    
    # Apply filters
    if status and status != 'all':
        query = query.filter(Task.status == status)
    
    if priority and priority != 'all':
        query = query.filter(Task.priority == priority)
    
    if category and category != 'all':
        query = query.filter(Task.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Task.title.ilike(search_term)) | 
            (Task.description.ilike(search_term))
        )
    
    # Order by created_at descending (newest first)
    tasks = query.order_by(Task.created_at.desc()).all()
    
    return jsonify([task.to_dict() for task in tasks])

@task_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    data = request.json
    
    # Parse due_date if provided
    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400
    
    task = Task(
        title=data['title'],
        description=data.get('description', ''),
        priority=data.get('priority', 'medium'),
        status=data.get('status', 'pending'),
        category=data.get('category', 'personal'),
        due_date=due_date
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify(task.to_dict()), 201

@task_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task by ID"""
    task = Task.query.get_or_404(task_id)
    return jsonify(task.to_dict())

@task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update a specific task"""
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    # Update fields if provided
    task.title = data.get('title', task.title)
    task.description = data.get('description', task.description)
    task.priority = data.get('priority', task.priority)
    task.status = data.get('status', task.status)
    task.category = data.get('category', task.category)
    
    # Handle due_date update
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid due_date format. Use YYYY-MM-DD'}), 400
        else:
            task.due_date = None
    
    # Update timestamp
    task.updated_at = datetime.utcnow()
    
    db.session.commit()
    return jsonify(task.to_dict())

@task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a specific task"""
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return '', 204

@task_bp.route('/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task_status(task_id):
    """Toggle task status between pending and completed"""
    task = Task.query.get_or_404(task_id)
    task.status = 'completed' if task.status == 'pending' else 'pending'
    task.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(task.to_dict())

@task_bp.route('/tasks/stats', methods=['GET'])
def get_task_stats():
    """Get task statistics"""
    total_tasks = Task.query.count()
    completed_tasks = Task.query.filter(Task.status == 'completed').count()
    pending_tasks = Task.query.filter(Task.status == 'pending').count()
    
    # Count overdue tasks (pending tasks with due_date in the past)
    today = date.today()
    overdue_tasks = Task.query.filter(
        Task.status == 'pending',
        Task.due_date < today
    ).count()
    
    # Priority breakdown
    high_priority = Task.query.filter(Task.priority == 'high').count()
    medium_priority = Task.query.filter(Task.priority == 'medium').count()
    low_priority = Task.query.filter(Task.priority == 'low').count()
    
    # Category breakdown
    work_tasks = Task.query.filter(Task.category == 'work').count()
    personal_tasks = Task.query.filter(Task.category == 'personal').count()
    shopping_tasks = Task.query.filter(Task.category == 'shopping').count()
    
    return jsonify({
        'total': total_tasks,
        'completed': completed_tasks,
        'pending': pending_tasks,
        'overdue': overdue_tasks,
        'completion_rate': round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
        'priority_breakdown': {
            'high': high_priority,
            'medium': medium_priority,
            'low': low_priority
        },
        'category_breakdown': {
            'work': work_tasks,
            'personal': personal_tasks,
            'shopping': shopping_tasks
        }
    })

@task_bp.route('/tasks/bulk', methods=['DELETE'])
def bulk_delete_tasks():
    """Delete multiple tasks by IDs"""
    data = request.json
    task_ids = data.get('task_ids', [])
    
    if not task_ids:
        return jsonify({'error': 'No task IDs provided'}), 400
    
    deleted_count = Task.query.filter(Task.id.in_(task_ids)).delete(synchronize_session=False)
    db.session.commit()
    
    return jsonify({'deleted_count': deleted_count})

@task_bp.route('/tasks/bulk/status', methods=['PATCH'])
def bulk_update_status():
    """Update status for multiple tasks"""
    data = request.json
    task_ids = data.get('task_ids', [])
    new_status = data.get('status')
    
    if not task_ids or not new_status:
        return jsonify({'error': 'task_ids and status are required'}), 400
    
    if new_status not in ['pending', 'completed']:
        return jsonify({'error': 'Invalid status. Must be pending or completed'}), 400
    
    updated_count = Task.query.filter(Task.id.in_(task_ids)).update(
        {'status': new_status, 'updated_at': datetime.utcnow()},
        synchronize_session=False
    )
    db.session.commit()
    
    return jsonify({'updated_count': updated_count})

