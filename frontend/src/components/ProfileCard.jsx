import React from 'react';

const ProfileCard = ({ profile }) => {
  const pills = [
    { label: 'Diagnosis', value: profile.primary_diagnosis },
    { label: 'Stage', value: profile.stage_or_severity || 'N/A' },
    { label: 'Markers', value: profile.molecular_markers || 'Not specified' },
    { label: 'ECOG', value: profile.performance_status || 'Not specified' },
  ];

  return (
    <div className="mb-8 p-4 bg-red-50 rounded-lg border border-red-200">
      <h3 className="text-sm font-semibold text-red-900 mb-4">Patient Profile</h3>
      <div className="flex flex-wrap gap-2">
        {pills.map((pill, idx) => (
          <div key={idx} className="inline-flex items-center gap-1">
            <span className="text-xs font-medium text-red-700 bg-red-100 px-2 py-1 rounded">
              {pill.label}: <strong className="ml-1">{pill.value}</strong>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProfileCard;
