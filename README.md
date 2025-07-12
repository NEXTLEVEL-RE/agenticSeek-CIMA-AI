# Real Estate Wholesale Business Management System

A comprehensive full-stack application for managing wholesale real estate business operations, including property management, lead tracking, deal pipeline, and financial analytics.

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)
- **Framework**: FastAPI with Python 3.8+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with bcrypt password hashing
- **API Documentation**: Automatic OpenAPI/Swagger docs

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React Query for server state
- **Routing**: React Router DOM
- **UI Components**: Custom components with Headless UI

## 🚀 Features

### Core Functionality
- **User Management**: Role-based access (Admin, Agent, Investor)
- **Property Management**: Track properties with financial details
- **Lead Management**: Comprehensive lead tracking and follow-up
- **Deal Pipeline**: Manage deals from initial contact to closing
- **Financial Analytics**: Revenue tracking and profit calculations
- **Dashboard**: Real-time business metrics and insights

### Business Features
- **Wholesale Fee Calculation**: Automatic 10% wholesale fee calculation
- **ARV Tracking**: After Repair Value management
- **Deal Status Tracking**: Pending, Approved, Rejected, Closed
- **Lead Status Management**: New, Contacted, Interested, Not Interested, Converted
- **Property Status**: Available, Under Contract, Sold, Off Market

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd real-estate-wholesale-app
```

### 2. Backend Setup

#### Install Python Dependencies
```bash
cd real_estate_backend
pip install -r requirements.txt
```

#### Database Setup
1. Create PostgreSQL database:
```sql
CREATE DATABASE real_estate_db;
CREATE USER real_estate_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE real_estate_db TO real_estate_user;
```

2. Update database configuration in `app/config.py`:
```python
DATABASE_URL = "postgresql://real_estate_user:your_password@localhost/real_estate_db"
```

3. Create environment variables (optional):
```bash
# Create .env file
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://real_estate_user:your_password@localhost/real_estate_db
```

#### Run Backend
```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python main.py
```

### 3. Frontend Setup

#### Install Node.js Dependencies
```bash
cd real_estate_frontend
npm install
```

#### Environment Configuration
Create `.env` file in frontend directory:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

#### Run Frontend
```bash
npm run dev
```

## 🌐 Access Points

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/token` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user

### Properties
- `GET /api/v1/properties` - List properties
- `POST /api/v1/properties` - Create property
- `GET /api/v1/properties/{id}` - Get property
- `PUT /api/v1/properties/{id}` - Update property
- `DELETE /api/v1/properties/{id}` - Delete property
- `GET /api/v1/properties/search` - Search properties

### Leads
- `GET /api/v1/leads` - List leads
- `POST /api/v1/leads` - Create lead
- `GET /api/v1/leads/{id}` - Get lead
- `PUT /api/v1/leads/{id}` - Update lead
- `DELETE /api/v1/leads/{id}` - Delete lead
- `PUT /api/v1/leads/{id}/status` - Update lead status

### Deals
- `GET /api/v1/deals` - List deals
- `POST /api/v1/deals` - Create deal
- `GET /api/v1/deals/{id}` - Get deal
- `PUT /api/v1/deals/{id}` - Update deal
- `DELETE /api/v1/deals/{id}` - Delete deal
- `PUT /api/v1/deals/{id}/status` - Update deal status
- `GET /api/v1/deals/analytics/summary` - Deal analytics

### Dashboard
- `GET /api/v1/dashboard/stats` - Dashboard statistics
- `GET /api/v1/dashboard/recent-activity` - Recent activity
- `GET /api/v1/dashboard/property-status-distribution` - Property status chart
- `GET /api/v1/dashboard/lead-status-distribution` - Lead status chart
- `GET /api/v1/dashboard/deal-status-distribution` - Deal status chart
- `GET /api/v1/dashboard/monthly-revenue` - Monthly revenue data

## 🗄️ Database Schema

### Users Table
- id, email, username, hashed_password, full_name, role, phone, is_active, created_at, updated_at

### Properties Table
- id, address, city, state, zip_code, property_type, square_feet, bedrooms, bathrooms, year_built
- arv, purchase_price, repair_cost, holding_cost, selling_price
- status, owner_id, list_date, sold_date, description, notes, created_at, updated_at

### Leads Table
- id, first_name, last_name, email, phone, address, city, state, zip_code
- property_type, estimated_value, reason_for_selling, timeline
- status, assigned_to_id, notes, next_follow_up, created_at, updated_at

### Deals Table
- id, property_id, lead_id, agent_id, status, offer_price, closing_date
- wholesale_fee, net_profit, notes, created_at, updated_at

## 🎨 Frontend Structure

```
src/
├── components/     # Reusable UI components
├── contexts/      # React contexts (Auth, etc.)
├── lib/          # API client and utilities
├── pages/        # Page components
├── types/        # TypeScript type definitions
└── App.tsx       # Main app component
```

## 🔧 Development

### Backend Development
```bash
# Run with auto-reload
uvicorn main:app --reload

# Run tests
pytest

# Database migrations (when needed)
alembic upgrade head
```

### Frontend Development
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 🚀 Deployment

### Backend Deployment
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `alembic upgrade head`
5. Start server: `uvicorn main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment
1. Build the application: `npm run build`
2. Serve the `dist` folder with a web server
3. Configure API URL in environment variables

## 📈 Business Features

### Wholesale Calculations
- **Wholesale Fee**: 10% of ARV (After Repair Value)
- **Net Profit**: Wholesale Fee - (Offer Price - Purchase Price)
- **ROI Tracking**: Automatic calculation of return on investment

### Lead Management
- **Status Tracking**: New → Contacted → Interested → Converted
- **Follow-up Scheduling**: Automated reminders for lead follow-up
- **Lead Scoring**: Based on property value and timeline

### Deal Pipeline
- **Status Management**: Pending → Approved → Closed
- **Financial Tracking**: Offer price, closing costs, net profit
- **Timeline Management**: Closing date tracking

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy

## 📱 Responsive Design

- Mobile-first approach
- Tailwind CSS for responsive design
- Modern UI components
- Accessibility features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the code comments for implementation details

---

**Built with ❤️ for Real Estate Wholesale Professionals**