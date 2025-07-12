import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Total Properties</h3>
          <p className="text-3xl font-bold text-primary-600">0</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Total Leads</h3>
          <p className="text-3xl font-bold text-success-600">0</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Total Deals</h3>
          <p className="text-3xl font-bold text-warning-600">0</p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900">Revenue</h3>
          <p className="text-3xl font-bold text-primary-600">$0</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 