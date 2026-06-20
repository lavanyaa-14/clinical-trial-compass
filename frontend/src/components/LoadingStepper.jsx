import React from 'react';

const LoadingStepper = () => {
  const [activeStep, setActiveStep] = React.useState(0);

  React.useEffect(() => {
    if (activeStep < 2) {
      const timeout = activeStep === 0 ? 1500 : 3000;
      const timer = setTimeout(() => setActiveStep(activeStep + 1), timeout);
      return () => clearTimeout(timer);
    }
  }, [activeStep]);

  const steps = [
    'Synthesizing search query...',
    'Searching trial database...',
    'Ranking matches...',
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-red-50 to-white p-4">
      <div className="max-w-2xl mx-auto mt-16">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-red-900 mb-8 text-center">
            Finding your matches
          </h2>

          <div className="space-y-4">
            {steps.map((step, idx) => (
              <div key={idx} className="flex items-center gap-4">
                <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-red-600 text-white font-medium">
                  {idx < activeStep ? (
                    <span className="text-xl">✓</span>
                  ) : idx === activeStep ? (
                    <div className="w-6 h-6 border-3 border-red-300 border-t-white rounded-full animate-spin"></div>
                  ) : (
                    <span>{idx + 1}</span>
                  )}
                </div>
                <span className={`text-lg ${idx <= activeStep ? 'text-gray-800 font-medium' : 'text-gray-400'}`}>
                  {step}
                </span>
              </div>
            ))}
          </div>

          <p className="text-center text-gray-500 text-sm mt-8">
            This typically takes 10-15 seconds
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoadingStepper;
