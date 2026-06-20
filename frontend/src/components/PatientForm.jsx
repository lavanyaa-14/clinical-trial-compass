import React, { useState } from 'react';

const PatientForm = ({ onSubmit, isLoading }) => {
  const [formData, setFormData] = useState({
    age: '',
    sex: 'Male',
    primary_diagnosis: '',
    stage_or_severity: '',
    molecular_markers: '',
    prior_treatments: '',
    current_medications: '',
    performance_status: '',
    additional_notes: '',
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const fillSamplePatient = () => {
    setFormData({
      age: 58,
      sex: 'Female',
      primary_diagnosis: 'Non-small cell lung cancer (NSCLC)',
      stage_or_severity: 'Stage II',
      molecular_markers: 'EGFR exon 19 deletion (positive)',
      prior_treatments: 'None',
      current_medications: 'Lisinopril 10mg, Metformin 500mg',
      performance_status: 'ECOG 1',
      additional_notes: 'No brain metastases on recent MRI',
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validate required fields
    if (!formData.age || !formData.primary_diagnosis) {
      alert('Please fill in age and primary diagnosis');
      return;
    }

    onSubmit({
      ...formData,
      age: parseInt(formData.age, 10),
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-white p-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-red-900 mb-2">ClinicalTrialCompass</h1>
          <p className="text-gray-600 mb-8">Find clinical trials matched to your profile</p>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Age */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Age (years)
              </label>
              <input
                type="number"
                name="age"
                min="0"
                max="120"
                value={formData.age}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Enter age"
                required
              />
            </div>

            {/* Sex */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Sex
              </label>
              <select
                name="sex"
                value={formData.sex}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>

            {/* Primary diagnosis */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Primary diagnosis *
              </label>
              <input
                type="text"
                name="primary_diagnosis"
                value={formData.primary_diagnosis}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="e.g. Non-small cell lung cancer"
                required
              />
            </div>

            {/* Stage or severity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stage or severity
              </label>
              <input
                type="text"
                name="stage_or_severity"
                value={formData.stage_or_severity}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="e.g. Stage II, or N/A"
              />
            </div>

            {/* Molecular markers */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Molecular markers
              </label>
              <input
                type="text"
                name="molecular_markers"
                value={formData.molecular_markers}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="e.g. EGFR exon 19 deletion, or None known"
              />
            </div>

            {/* Prior treatments */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prior treatments
              </label>
              <input
                type="text"
                name="prior_treatments"
                value={formData.prior_treatments}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="e.g. None, or Carboplatin 2 cycles"
              />
            </div>

            {/* Current medications */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Current medications
              </label>
              <input
                type="text"
                name="current_medications"
                value={formData.current_medications}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="e.g. Lisinopril 10mg, Metformin 500mg"
              />
            </div>

            {/* Performance status */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Performance status
              </label>
              <input
                type="text"
                name="performance_status"
                value={formData.performance_status}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="e.g. ECOG 1, or Unknown"
              />
            </div>

            {/* Additional notes */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Additional notes
              </label>
              <textarea
                name="additional_notes"
                value={formData.additional_notes}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                placeholder="Any other relevant clinical information"
                rows="3"
              ></textarea>
            </div>

            {/* Buttons */}
            <div className="flex gap-4">
              <button
                type="submit"
                disabled={isLoading}
                className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-400 text-white font-bold py-3 px-4 rounded-lg transition"
              >
                {isLoading ? 'Matching...' : 'Find Matching Trials'}
              </button>
              <button
                type="button"
                onClick={fillSamplePatient}
                disabled={isLoading}
                className="px-6 bg-gray-300 hover:bg-gray-400 disabled:bg-gray-200 text-gray-800 font-medium py-3 rounded-lg transition"
              >
                Sample Patient
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default PatientForm;
