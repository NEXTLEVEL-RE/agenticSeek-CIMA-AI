export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: 'admin' | 'agent' | 'investor';
  phone?: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface Property {
  id: number;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  property_type: string;
  square_feet?: number;
  bedrooms?: number;
  bathrooms?: number;
  year_built?: number;
  arv?: number;
  purchase_price?: number;
  repair_cost?: number;
  holding_cost?: number;
  selling_price?: number;
  status: 'available' | 'under_contract' | 'sold' | 'off_market';
  owner_id: number;
  list_date: string;
  sold_date?: string;
  description?: string;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface Lead {
  id: number;
  first_name: string;
  last_name: string;
  email?: string;
  phone?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  property_type?: string;
  estimated_value?: number;
  reason_for_selling?: string;
  timeline?: string;
  status: 'new' | 'contacted' | 'interested' | 'not_interested' | 'converted';
  assigned_to_id?: number;
  notes?: string;
  next_follow_up?: string;
  created_at: string;
  updated_at?: string;
}

export interface Deal {
  id: number;
  property_id: number;
  lead_id: number;
  agent_id: number;
  status: 'pending' | 'approved' | 'rejected' | 'closed';
  offer_price: number;
  closing_date?: string;
  wholesale_fee?: number;
  net_profit?: number;
  notes?: string;
  created_at: string;
  updated_at?: string;
}

export interface DashboardStats {
  total_properties: number;
  available_properties: number;
  total_leads: number;
  new_leads: number;
  total_deals: number;
  pending_deals: number;
  total_revenue: number;
  monthly_revenue: number;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
} 